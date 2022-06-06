from requests import Request,Session
import requests
from requests import HTTPError
import json
import re
from datetime import datetime
class Instagram:

    USER_AGENT = "Mozilla/5.0 (Linux; Android 9; SM-G955U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.111 Mobile Safari/537.36 Instagram 153.0.0.34.96 Android (28/9; 420dpi; 1080x2094; samsung; SM-G955U; dream2qltesq; qcom; en_US; 236572377)"
    
    def __init__(self,config_file=False):
        
        self.session = Session()
        self.session.headers.update({'User-Agent':self.USER_AGENT})
        self.config_file = config_file
        self.username = ''
        self.password = ''
        if config_file:
            try:
                self.load_session_from_config()
            except FileNotFoundError:
                print("Config files not found... running for first time...")


    def load_session_from_config(self):

        if not self.config_file:
            raise ValueError("Config file not loaded")
        
        f = open("config_headers","r")

        data = f.read()
        if not data:
            raise ValueError("Headers File is empty")
        session = json.loads(data)
        
        self.session.headers.update(session)

        f.close()

        f = open("config_cookies","r")

        data = f.read()
        if not data:
            raise ValueError("Cookies File is empty")
        cookies = json.loads(data)
        
        self.session.cookies.update(cookies)

        f.close()
        return True


    def write_session_to_file(self):
        f = open("config_headers", "w")
        f.write(json.dumps(dict(self.session.headers)))
        f.close()
        f = open("config_cookies", "w")
        f.write(json.dumps(dict(self.session.cookies)))
        f.close()
  

    def get_ig_app_id_and_asbd(self):

        url = 'https://www.instagram.com/static/bundles/metro/ConsumerLibCommons.js/abe44afead26.js'

        response = requests.get(url, headers = {'User-agent' : self.USER_AGENT})
        
        js = response.text
        
        m = re.search('e.ASBD_ID ?= ?\'[0-9]+\'',js)
        m2 = re.search('[0-9]+',m.group(0))

        ASBD_ID = m2.group(0)
    
        m = re.search('instagramWebDesktopFBAppId ?= ?\'[0-9]+\'',js)
        m2 = re.search('[0-9]+',m.group(0))

        IG_APP_ID = m2.group(0)

        self.session.headers.update({'X-ASBD-ID':ASBD_ID,'X-IG-App-ID':IG_APP_ID})   


    def get_rollout_hash(self): 

        url = 'https://www.instagram.com/data/shared_data/'

        response = requests.get(url, headers = {'User-agent' : self.USER_AGENT})
        
        json_data = json.loads(response.text)

        rollout_hash = (json_data['rollout_hash'])

        self.session.headers.update({'X-Instagram-AJAX':rollout_hash})  
        
    
    def login(self,username=None, password=None) -> bool:

        if username is None:
            username = self.username
        if password is None:
            password = self.password

        url = 'https://www.instagram.com/accounts/login/'
        login_url = 'https://www.instagram.com/accounts/login/ajax/'

        time = int(datetime.now().timestamp())

        response = self.session.get(url)

        if response.status_code != 200:
            print('Error logging in: ',response)
            return False


        csrf = response.cookies['csrftoken']

        self.session.headers.update({'X-CSRFTOKEN':csrf})

        payload = {
            'username': username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        login_header = {
            #"User-Agent": 'lalalalal',
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "X-IG-WWW-Claim": '0'
            #"x-csrftoken": csrf,           
            #"X-ASBD-ID": session['X-ASBD-ID'],
            #"X-Instagram-AJAX": session['X-Instagram-AJAX'],
            #"X-IG-App-ID": session['X-IG-App-ID']
        }

        login_response = self.session.post(login_url, data=payload, headers=login_header)
        if login_response.status_code != 200:
            print('Error logging in: ',login_response)
            return False

        json_data = json.loads(login_response.text)

        if 'authenticated' in json_data:
            print("LOGIN SUCCESS")

            csrf = login_response.cookies['csrftoken']
            self.session.headers.update({'X-CSRFTOKEN':csrf})
            
            hmac = login_response.headers['x-ig-set-www-claim']
            self.session.headers.update({'X-IG-WWW-Claim':hmac})
           
            return True

        return False


    def upload_photo(self,photo,upload_id=None):

        upload_id = int(datetime.now().timestamp())
        upload_name = "fb_uploader_{upload_id}".format(upload_id=upload_id)
        rupload_params = {
            "media_type": "1",
            "upload_id": upload_id
        }

        photo_data = open(photo, "rb").read()
        photo_len = str(len(photo_data))
        headers = {
            #'X-Instagram-AJAX': session['X-Instagram-AJAX'], 
            #'X-IG-App-ID': session['X-IG-App-ID'],
            #'X-ASBD-ID': session['X-ASBD-ID'],
            "X-Instagram-Rupload-Params": json.dumps(rupload_params),
            "X-Entity-Type": "image/jpeg",
            "Offset": "0",
            "X-Entity-Name": upload_name,
            "X-Entity-Length": photo_len,
            "Content-Type": "application/octet-stream",
            "Content-Length": photo_len,
            "Accept-Encoding": "gzip",
        }

        response = self.session.request("POST", "https://i.instagram.com/rupload_igphoto/"+upload_name, headers=headers, data=photo_data)#, cookies=cookies)

        if response.status_code != 200:
            print("Photo Upload failed with the following response: {}".format(response))
            raise HTTPError("Status Code")

        upload_id = int(response.json()['upload_id'])
        return upload_id
    

    def upload_album(self,upload_ids,caption=""):

        upload_id = int(datetime.now().timestamp())

        children_metadata = [{"upload_id" : str(i)} for i in upload_ids] #these need to be strings (enclosed in quotes in JSON)
        
        data = json.dumps({
            "caption": caption,
            "children_metadata": children_metadata,
            "client_sidecar_id": str(upload_id), 
            "disable_comments": "0",
            "like_and_view_counts_disabled": False,
            "source_type": "library"
            
        })

        print(data)

        headers = {
            #'X-CSRFTOKEN': session['csrf_token'], 
            #'X-Instagram-AJAX': session['X-Instagram-AJAX'], 
            #'X-IG-App-ID': session['X-IG-App-ID'],
            #'X-ASBD-ID': session['X-ASBD-ID'],
            #'X-IG-WWW-Claim': session['X-IG-WWW-Claim'],
            "Accept-Encoding": "gzip",
            "Offset": "0",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip",
            "Content-Length": str(len(data))
        }

        response = self.session.request("POST", "https://i.instagram.com/api/v1/media/configure_sidecar/", headers=headers, data=data)#, cookies=cookies)
        print(response.request.headers)
        if response.status_code != 200:
            print(
                "Album Upload failed with the following response: {}".format(response)
            )
            return None
        
        upload_id = int(response.json()['client_sidecar_id'])

        return upload_id