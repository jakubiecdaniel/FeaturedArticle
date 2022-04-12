import requests
import json
from datetime import datetime
from uuid import uuid4
from typing import BinaryIO
from InstagramSession import InstagramSession
import re


session = {
    "csrf_token": "CSRF_TOKEN",
    "session_id": "SESSION_ID",
    "ds_user_id": "DS_USER_ID",
    "ig_did"    : "IG_DID",
    #"ig_nrcb"   : "IG_NRCB",
    "mid"       : "MID",
    "rur"       : "RUR",
}

USER_AGENT = "lalalalal"
USER_AGENT_2 = "Mozilla/5.0 (Linux; Android 9; SM-G955U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.111 Mobile Safari/537.36 Instagram 153.0.0.34.96 Android (28/9; 420dpi; 1080x2094; samsung; SM-G955U; dream2qltesq; qcom; en_US; 236572377)"

def get_ig_app_id_and_asbd(igSession=None):

    url = 'https://www.instagram.com/static/bundles/metro/ConsumerLibCommons.js/abe44afead26.js'

    response = requests.get(url, headers = {'User-agent' : USER_AGENT_2})

    js = response.text
    
    m = re.search('e.ASBD_ID ?= ?\'[0-9]+\'',js)
    m2 = re.search('[0-9]+',m.group(0))

    ASBD_ID = m2.group(0)
   
    m = re.search('instagramWebDesktopFBAppId ?= ?\'[0-9]+\'',js)
    m2 = re.search('[0-9]+',m.group(0))

    IG_APP_ID = m2.group(0)

    if igSession:
        igSession.set_value('X-ASBD-ID',ASBD_ID)
        igSession.set_value('X-IG-App-ID',IG_APP_ID)
    
    session['X-ASBD-ID'] = ASBD_ID
    session['X-IG-App-ID'] = IG_APP_ID

    return ASBD_ID, IG_APP_ID
    
#for gettng X-Instagram-AJAX
def get_rollout_hash(igSession=None): 

    url = 'https://www.instagram.com/data/shared_data/'

    response = requests.get(url, headers = {'User-agent' : USER_AGENT_2})

    json_data = json.loads(response.text)

    rollout_hash = (json_data['rollout_hash'])

    if igSession:
        igSession.set_value('X-Instagram-AJAX',rollout_hash)
    
    session['X-Instagram-AJAX'] = rollout_hash

    return rollout_hash

def login(username, password,igSession=None) -> bool:
    if igSession:
        session = igSession.session

    url = 'https://www.instagram.com/accounts/login/'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    time = int(datetime.now().timestamp())
    
    response = requests.get(url, headers = {'User-agent' : USER_AGENT_2})

    if response.status_code != 200:
        print('Error logging in: ',response)
        return False

    print("Login Response Reason: ",response.reason)
    csrf = response.cookies['csrftoken']

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    print(payload)

    login_header = {
        "User-Agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf,
        "X-IG-WWW-Claim": '0',
        "X-ASBD-ID": session['X-ASBD-ID'],
        "X-Instagram-AJAX": session['X-Instagram-AJAX'],
        "X-IG-App-ID": session['X-IG-App-ID']
    }

    login_response = requests.post(login_url, data=payload, headers=login_header)
    if login_response.status_code != 200:
        print('Error logging in: ',login_response)
        return False

    json_data = json.loads(login_response.text)

    try:
        if json_data["authenticated"]:
            print("LOGIN SUCCESS")

            cookies = login_response.cookies
            cookie_jar = cookies.get_dict()
 
            session = {
                "csrf_token": cookie_jar['csrftoken'],
                "session_id": cookie_jar['sessionid'],
                "ds_user_id": cookie_jar['ds_user_id'],
                "ig_did"    : cookie_jar['ig_did'],
                #"ig_nrcb"   : cookie_jar['ig_nrcb'],
                "mid"       : cookie_jar['mid'],
                "rur"       : cookie_jar['rur'],
                "X-IG-WWW-Claim" : login_response.headers['x-ig-set-www-claim']
            }

            if igSession is not None:
                igSession.update_session(session)

            return True
    except:
        print('Login Failed')

    return False



def upload_photo(photo,upload_id=None,igSession=None):
    if igSession:
        session = igSession.session

    upload_id = int(datetime.now().timestamp())

    upload_name = "fb_uploader_{upload_id}".format(upload_id=upload_id)
    rupload_params = {
        "media_type": "1",
        "upload_id": upload_id
    }

    photo_data = open(photo, "rb").read()
    photo_len = str(len(photo_data))

    headers = {
        'X-Instagram-AJAX': session['X-Instagram-AJAX'], 
        'X-IG-App-ID': session['X-IG-App-ID'],
        'X-ASBD-ID': session['X-ASBD-ID'],
        "Accept-Encoding": "gzip",
        "X-Instagram-Rupload-Params": json.dumps(rupload_params),
        "X-Entity-Type": "image/jpeg",
        "Offset": "0",
        "X-Entity-Name": upload_name,
        "X-Entity-Length": photo_len,
        "Content-Type": "application/octet-stream",
        "Content-Length": photo_len,
        "Accept-Encoding": "gzip",
    }
    cookies = {
        "sessionid": session['session_id'],
        "csrftoken": session['csrf_token'],
        'ds_user_id':session['ds_user_id'],
        'ig_did=':  session['ig_did'],
        'ig_nrcb1': '1',
        'mid': session['mid'],
        'rur': session['rur']
    }

    response = requests.request("POST", "https://i.instagram.com/rupload_igphoto/"+upload_name, headers=headers, data=photo_data, cookies=cookies)
   
    if response.status_code != 200:
        print(
            "Photo Upload failed with the following response: {}".format(response)
        )
        return None
   
    upload_id = int(response.json()['upload_id'])

    return upload_id
   



def post(upload_id,caption="",igSession=None):

    if igSession:
        session = igSession.session

    url = "https://www.instagram.com/create/configure/"

    payload = f'upload_id={upload_id}&caption={caption}&usertags=&custom_accessibility_caption=&retry_timeout='
    headers = {
        'authority': 'www.instagram.com',
        'x-ig-www-claim': session['X-IG-WWW-Claim'], 
        'X-Instagram-AJAX': session['X-Instagram-AJAX'], 
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'user-agent': USER_AGENT_2,
        'x-requested-with': 'XMLHttpRequest',
        'x-csrftoken': session['csrf_token'],
        'x-ig-app-id': session['X-IG-App-ID'],
        'origin': 'https://www.instagram.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.instagram.com/create/details/',
        'accept-language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
    }

    cookies = {
        "sessionid": session['session_id'],
        "csrftoken": session['csrf_token']
    }

    response = requests.request("POST", url, headers=headers, data=payload, cookies=cookies)

    json_data = json.loads(response.text)

    print(json_data)


def upload_album(upload_ids,caption="",igSession=None):

    if igSession:
        session = igSession.session

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
        'X-CSRFTOKEN': session['csrf_token'], 
        'X-Instagram-AJAX': session['X-Instagram-AJAX'], 
        'X-IG-App-ID': session['X-IG-App-ID'],
        'X-ASBD-ID': session['X-ASBD-ID'],
        'X-IG-WWW-Claim': session['X-IG-WWW-Claim'],
        "Accept-Encoding": "gzip",
        "Offset": "0",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        "Content-Length": str(len(data))
    }
    cookies = {
        "sessionid": session['session_id'],
        "csrftoken": session['csrf_token'],
        'ds_user_id':session['ds_user_id'],
        'ig_did=':  session['ig_did'],
        'ig_nrcb1': '1',
        'mid': session['mid'],
        'rur': session['rur']
    }

    response = requests.request("POST", "https://i.instagram.com/api/v1/media/configure_sidecar/", headers=headers, data=data, cookies=cookies)
   
    if response.status_code != 200:
        print(
            "Album Upload failed with the following response: {}".format(response)
        )
        return None
    
    upload_id = int(response.json()['client_sidecar_id'])

    return upload_id

