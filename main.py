
import ImageUtils
import Wikipedia
import InstagramUtils
import sys

article = ''

def run(username,password):

    #Get URL
    global article
    article = Wikipedia.GetFeaturedArticleURL()

    #Take screenshot
    image_path = Wikipedia.TakePicture(article)

    #Convert to JPG
    image_path = ImageUtils.PNGtoJPG(image_path, 'sc.jpg')

    images = (ImageUtils.SplitAndCrop('sc.png'))

    run2(images,username,password)

#Run()

#images = ['./output\\post_01.png', './output\\post_02.png', './output\\post_03.png', './output\\post_04.png', './output\\post_05.png', './output\\post_06.png', './output\\post_07.png', './output\\post_08.png', './output\\post_09.png', './output\\post_10.png', './output\\post_11.png']

def run2(images,username,password):

    #InstagramUtils.login(username,password)
    #image = open(images[0],'rb')
    #InstagramUtils.upload_photo(images[0])

    from InstagramSession import InstagramSession

    s = InstagramSession()

    if not s.load_from_file():
        InstagramUtils.get_ig_app_id_and_asbd(s)
        InstagramUtils.get_rollout_hash(s)
        InstagramUtils.login(username,password,s)
        s.write_to_file()
        
    ids = []

    for image_path in images:
        image_path_2 = ImageUtils.PNGtoJPG(image_path,'a.jpg')
        ids.append(InstagramUtils.upload_photo(image_path_2,igSession=s))
    
    if ids:
        InstagramUtils.upload_album(ids,caption=article,igSession=s)

#



if __name__ == '__main__':
    run(sys.argv[1],sys.argv[2])