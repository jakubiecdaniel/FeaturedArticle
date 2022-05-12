
import ImageUtils
import Wikipedia
import Instagram
import sys
import os
from requests import HTTPError


def login(insta):
    insta.get_ig_app_id_and_asbd()
    
    insta.get_rollout_hash()
    
    insta.login()
    insta.write_session_to_file()

def do_upload(insta,images,article):
    ids = []

    for image_path in images:
        ImageUtils.PNGtoJPG(image_path,'a.jpg')
        #ImageUtils.resize('a.jpg')
        ids.append(insta.upload_photo('a.jpg'))
    
    if ids: #400 occurs when images are too big
        insta.upload_album(ids,caption=article)

def do_wikipedia():
    ImageUtils.clear_output_folder()

    article = Wikipedia.GetFeaturedArticleURL()
    if not article:
        return

    image_path = Wikipedia.chrome_headless_picture(article)
    if not image_path:
        return

    ImageUtils.PNGtoJPG(image_path, 'sc.jpg')

    images = (ImageUtils.SplitAndCrop('sc.jpg'))
    
    return images,article
    

#images = ['./output\\post_01.png', './output\\post_02.png', './output\\post_03.png', './output\\post_04.png', './output\\post_05.png', './output\\post_06.png', './output\\post_07.png', './output\\post_08.png', './output\\post_09.png', './output\\post_10.png', './output\\post_11.png']



def run(username,password):

    insta = Instagram.Instagram(True)
    insta.username = username
    insta.password = password
    images,article = do_wikipedia()
    try:
        do_upload(insta,images,article)
    except HTTPError:
        login(insta)
        do_upload(insta,images,article)
        
    





if __name__ == '__main__':
    try:
        run(sys.argv[1],sys.argv[2])
    except IndexError:
        print("Username/Password environment variables not found")
    
    
   