import json
from datetime import datetime
from typing import BinaryIO
import requests

import imghdr
import os
import shutil
import struct

import time
import random

from uuid import uuid4


session = {
    "csrf_token": "CSRF_TOKEN",
    "session_id": "SESSION_ID"
}


def login(username,password):
    url = 'https://www.instagram.com/accounts/login/'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    time = int(datetime.now().timestamp())

    response = requests.get(url, headers = {'User-agent' : 'lalalalala'})
    csrf = response.cookies['csrftoken']

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    login_header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/77.0.3865.120 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    }

    login_response = requests.post(login_url, data=payload, headers=login_header)
    json_data = json.loads(login_response.text)



    if json_data["authenticated"]:
        print(json_data)
        cookies = login_response.cookies
        cookie_jar = cookies.get_dict()

        global session
        session = {
            "csrf_token": cookie_jar['csrftoken'],
            "session_id": cookie_jar['sessionid']
        }

def UploadPhoto(photo: BinaryIO) :

    micro_time = int(datetime.now().timestamp())

    headers = {
        "content-type": "image / png",
        "content-length": "1",
        "X-Entity-Name": f"fb_uploader_{micro_time}",
        "Offset": "0",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/77.0.3865.120 Safari/537.36",
        "x-entity-length": "1",
        "X-Instagram-Rupload-Params": f'{{"media_type": 1, "upload_id": {micro_time}, "upload_media_height": 1080,'
                                      f' "upload_media_width": 1080}}',
        "x-csrftoken": session['csrf_token'],
        "x-ig-app-id": "1217981644879628",
    }

    cookies = {
        "sessionid": session['session_id'],
        "csrftoken": session['csrf_token']
    }

    upload_response = requests.post(f'https://www.instagram.com/rupload_igphoto/fb_uploader_{micro_time}',
                                    data=photo, headers=headers, cookies=cookies)

    json_data = json.loads(upload_response.text)
    
    if json_data["status"] == "ok":
        upload_id = json_data['upload_id']
        return upload_id



def post(upload_id,caption=""):

    url = "https://www.instagram.com/create/configure/"

    payload = f'upload_id={upload_id}&caption={caption}&usertags=&custom_accessibility_caption=&retry_timeout='
    headers = {
        'authority': 'www.instagram.com',
        'x-ig-www-claim': 'hmac.AR2-43UfYbG2ZZLxh-BQ8N0rqGa-hESkcmxat2RqMAXejXE3',
        'x-instagram-ajax': 'adb961e446b7-hot',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.121 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-csrftoken': session['csrf_token'],
        'x-ig-app-id': '1217981644879628',
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



def upload_photo(
        photo,
        caption=None,
        upload_id=None,
        options={},
        is_sidecar=False
):
    options = dict({"configure_timeout": 15, "rename": True}, **(options or {}))

    waterfall_id = str(uuid4())
    # upload_name example: '1576102477530_0_7823256191'
    # upload_name example:  'fb_uploader_1585807380927'
    upload_name = "fb_uploader_{upload_id}".format(upload_id=upload_id)
    rupload_params = {
        "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
        "media_type": "1",
        "xsharing_user_ids": "[]",
        "upload_id": upload_id,
        "image_compression": json.dumps(
            {"lib_name": "moz", "lib_version": "3.1.m", "quality": "80"}
        ),
    }
    if is_sidecar:
        rupload_params["is_sidecar"] = "1"
    photo_data = open(photo, "rb").read()
    photo_len = str(len(photo_data))
    headers = {
        "Accept-Encoding": "gzip",
        "X-Instagram-Rupload-Params": json.dumps(rupload_params),
        "X_FB_PHOTO_WATERFALL_ID": waterfall_id,
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
        "csrftoken": session['csrf_token']
    }

    response = requests.request("POST", "https://www.instagram.com/rupload_igphoto/"+upload_name, headers=headers, data=photo_data, cookies=cookies)
    #response = self.session.post(
    #    "https://{domain}/rupload_igphoto/{name}".format(
    #        domain=config.API_DOMAIN, name=upload_name
    #    ),
    #    data=photo_data,
    #)

    if response.status_code != 200:
        print(
            "Photo Upload failed with the following response: {}".format(response)
        )
        return False
    # update the upload id
    upload_id = int(response.json()['upload_id'])

    # CONFIGURE

    return False

def upload_album(
        photos,
        caption=None,
        upload_id=None,
        from_video=False,
        force_resize=False,
        options={},
        user_tags=None
):
    if not photos:
        return False
    photo_metas = []
    for photo in photos:
        result = upload_photo(photo, caption, None, options, is_sidecar=True)
        if not result:
            print("Could not upload photo {photo} for the album!".format(photo=photo))
            return False
        photo_metas.append(result)
    if upload_id is None:
        upload_id = int(time.time() * 1000)
    data = json.dumps({
        "caption": caption,
        "client_sidecar_id": upload_id,
        "children_metadata": photo_metas
    })
    cookies = {
        "sessionid": session['session_id'],
        "csrftoken": session['csrf_token']
    }
    response = requests.request("POST", "https://i.instagram.com/api/v1/configure_sidecar/?", data=data, cookies=cookies)
    #return self.send_request("media/configure_sidecar/?", post=data)



