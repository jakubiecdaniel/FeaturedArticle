
import ImageUtils
import Wikipedia
import InstagramUtils
import sys

def run(username,password):
    ImageUtils.clear_output_folder()

    article = Wikipedia.GetFeaturedArticleURL()
    if not article:
        return

    image_path = Wikipedia.chrome_headless_picture(article)
    if not image_path:
        return

    ImageUtils.PNGtoJPG(image_path, 'sc.jpg')

    images = (ImageUtils.SplitAndCrop('sc.jpg'))
    print("images",images)
    run2(images,username,password,article)

#Run()

#images = ['./output\\post_01.png', './output\\post_02.png', './output\\post_03.png', './output\\post_04.png', './output\\post_05.png', './output\\post_06.png', './output\\post_07.png', './output\\post_08.png', './output\\post_09.png', './output\\post_10.png', './output\\post_11.png']

def run2(images,username,password,article):

    #InstagramUtils.login(username,password)
    #image = open(images[0],'rb')
    #InstagramUtils.upload_photo(images[0])

    from InstagramSession import InstagramSession

    s = InstagramSession()

    #if not s.load_from_file():
    InstagramUtils.get_ig_app_id_and_asbd(s)
    InstagramUtils.get_rollout_hash(s)
    InstagramUtils.login(username,password,s)
    s.write_to_file()
        
    ids = []

    for image_path in images:
        ImageUtils.PNGtoJPG(image_path,'a.jpg')
        #ImageUtils.resize('a.jpg')
        ids.append(InstagramUtils.upload_photo('a.jpg',igSession=s))
    
    if ids: #400 occurs when images are too big
        InstagramUtils.upload_album(ids,caption=article,igSession=s)

#



if __name__ == '__main__':
    #article = Wikipedia.GetFeaturedArticleURL()
    #Wikipedia.headless_pic(article)
    run(sys.argv[1],sys.argv[2])
    #ImageUtils.clear_output_folder()
   