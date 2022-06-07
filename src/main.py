
import ImageUtils
import Wikipedia
import Instagram
import sys
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

        ids.append(insta.upload_photo('a.jpg'))
    
    if ids: 
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

def run(username,password):

    cached_login = True
    insta = None
    
    try:
        insta = Instagram.Instagram(True)
    except ValueError:
        insta = Instagram.Instagram(False)
        cached_login = False

    insta.username = username
    insta.password = password
    images,article = do_wikipedia()

    if cached_login is True:
        try:
            do_upload(insta,images,article)
        except HTTPError:
            login(insta)
            do_upload(insta,images,article)
    else:
        login(insta)
        do_upload(insta,images,article)
        
if __name__ == '__main__':
    
    try:
        run(sys.argv[1],sys.argv[2])
    except IndexError:
        print("Username/Password environment variables not found")
     
    
   