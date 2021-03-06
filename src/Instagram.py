from requests import Request,Session
import requests
from requests import HTTPError
import json
import re
from datetime import datetime
class Instagram:

    class EditProfile:

        def __init__(self,json_data):
            #form_data = (json_data['entry_data']['SettingsPages'][0]['form_data'])
            form_data = json_data
            
            self.first_name = form_data['first_name']
            self.email = form_data['email']
            self.username = form_data['username']
            self.phone_number = form_data['phone_number']
            self.biography = form_data['biography']
            self.external_url = form_data['external_url']
            self.chaining_enabled = "On" if form_data['chaining_enabled'] else ""

        def update_external_url(self,url):
            self.external_url = url

        def get_json(self):
            return json.dumps(self.__dict__)

        def get_payload(self):

            payload = ''
            i = 0
            for key, value in self.__dict__.items():
                if i > 0:
                    payload += '&'
                payload += f'{key}={value}'
                i += 1

            return payload



    hashtag_list = ["#wikipedia","#education","#learning"]

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

    def get_session(self):
        return self.session


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

    def check_if_logged_in(self):
        not_logged_in_text = "not-logged-in"
        url = "https://www.instagram.com/"

        response = self.session.request("GET",url)
        if response.status_code != 200:
            print("Failed to check login status: {}".format(response))
            raise HTTPError 

        if not_logged_in_text in response.text:
            return False
        return True
        
    
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

        #try:
        #    self.update_link_in_bio(caption)
        #except (HTTPError, KeyError):
        #    print("Skipping updating link in bio...")

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


    def delete_post(self,post_id):
        #https://www.instagram.com/create/2836246768683468316/delete/?__d=dis

        url = f'https://www.instagram.com/create/{post_id}/delete/?__d=dis'

        response = self.session.request("POST", url)
        
        if response.status_code != 200:
            if response.status_code == 429:
                raise HTTPError
            print("Failed to Delete Post: {}".format(response))
            return
        
    def delete_all_posts(self,username):

        has_next = True
        post_ids = []
        loop_counter = 0
        user_id = ''
        cursor = ''
        while has_next:
            if loop_counter == 0:
                url = "https://i.instagram.com/api/v1/users/web_profile_info/?username=" + username
                
            else:
                url = f"https://www.instagram.com/graphql/query/?query_hash=69cba40317214236af40e7efa697781d&variables={{\"id\":\"{user_id}\",\"first\":12,\"after\":\"{cursor}\"}}"

            response = self.session.request("GET", url)
            if response.status_code != 200:
                print("Failed to Get Account: {}".format(response))
                return None
            json_data = response.json()
            if loop_counter == 0:
                user_id = json_data['data']['user']['id']
        
            post_data = json_data['data']['user']['edge_owner_to_timeline_media']

            posts = post_data['edges']
            page_info = post_data['page_info']
            cursor = page_info['end_cursor']
            has_next = page_info['has_next_page']
            
            index = 0
            while True:
                try:
                    id = posts[index]['node']['id']
                except IndexError:
                    break

                post_ids.append(id)
                index += 1

            loop_counter += 1

        for post in post_ids:
            
            self.delete_post(post)


    def update_link_in_bio(self,link_url):
        #url = "https://www.instagram.com/accounts/edit/"
        get_data_url = "https://i.instagram.com/api/v1/accounts/edit/web_form_data/"
        save_data_url = "https://www.instagram.com/accounts/edit/"

        response = self.session.request("GET",get_data_url)
        if response.status_code != 200:
            print("Failed to get profile data: {}".format(response))
            raise HTTPError

        #html = response.text
        #m = re.search('(<script type="text/javascript">window._sharedData =) ({.*)(;</script>)',html)
        #if m is None:
        #   raise ValueError
        #json_data = json.loads(m.group(2))
        
        json_data = json.loads(response.text)["form_data"]
        
        profile = self.EditProfile(json_data)
        profile.update_external_url(link_url)

        payload = profile.get_payload()

        headers = {
            "Content-Type":"application/x-www-form-urlencoded"
        }

        response = self.session.request("POST",save_data_url,headers=headers,json=payload)

        if response.status_code != 200:
            print("Failed to update profile data: {}".format(response))
            raise HTTPError

        

def login_to_instagram(username,password,use_cache=False):

    insta = None

    if use_cache == True:
        try:
            insta = Instagram(True)
        except ValueError:
            insta = Instagram(False)
            use_cache = False
    else:
        insta = Instagram(False)

    insta.username = username
    insta.password = password

    logged_in = False
    if use_cache == True:
        logged_in = insta.check_if_logged_in()

    if not logged_in:
        insta.get_ig_app_id_and_asbd()
        insta.get_rollout_hash()
        insta.login()
        insta.write_session_to_file()
        logged_in = insta.check_if_logged_in()
        if not logged_in:
            raise RuntimeError("Could Not Log in to Instagram")

    return insta

    
            