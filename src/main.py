
import ImageUtils
import Wikipedia
import Instagram
import sys

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

if __name__ == '__main__':
    
    username = ''
    password = ''
    try:
        username = sys.argv[1]
        password = sys.argv[2]
    except IndexError:
        print("Usage: py main.py username password")
        exit()

    insta = Instagram.login_to_instagram(username,password,False)
    images,article = do_wikipedia()
    do_upload(insta,images,article)
    #run(username,password)
    
     
    
   