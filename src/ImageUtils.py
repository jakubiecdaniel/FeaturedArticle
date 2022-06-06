from PIL import Image
import cv2
import os
import glob

#https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
def clear_output_folder(folder='./output'):

    files = glob.glob(folder+'/*')
    for f in files:
        os.remove(f)


def PNGtoJPG(image_path,image_new_path):

    png_img = cv2.imread(image_path)

    cv2.imwrite(image_new_path, png_img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])


def resize(image_path,image_new_width,image_new_height):

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    #height, width, _ = img.shape
    
    dim = (int(image_new_width),int(image_new_height))
    resized = cv2.resize(img,dim, interpolation=cv2.INTER_AREA)

    cv2.imwrite(image_path,resized)


def cropHeight(image_path,image_new_height):
    img = Image.open(image_path)
    width, _ = img.size
    crop = img.crop((0, 0, width, image_new_height))
    crop.save(image_path)


def SplitAndCrop(image_path):
    OUTPUT_DIR = './output'
    MIN_ASPECT_RATIO = .8
    MAX_ASPECT_RATIO = 1.91
    NUM_IMAGES = 10

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    images = []

    img = Image.open(image_path)
    width, height = img.size

    #aspect ratio has to be between 1.91 and .8
    #https://help.instagram.com/1631821640426723
    original_aspect_ratio = width/height
    print(original_aspect_ratio)
    if original_aspect_ratio < (MIN_ASPECT_RATIO / NUM_IMAGES) or original_aspect_ratio > (MAX_ASPECT_RATIO / NUM_IMAGES):
        if original_aspect_ratio < (MIN_ASPECT_RATIO / NUM_IMAGES) :
            new_height = width/(MIN_ASPECT_RATIO / NUM_IMAGES)

        elif original_aspect_ratio > 1.91:
            new_height = width/1.91

        cropHeight(image_path,new_height)
        img = Image.open(image_path)
        width, height = img.size

    
    w,h = (width,int(height / NUM_IMAGES))

    aspect_ratio = w/h

    print(aspect_ratio)

    frame_num = 1
    for col_i in range(0, width, w):
        for row_i in range(0, height, h):
            crop = img.crop((col_i, row_i, col_i + w, row_i + h))
            save_to= os.path.join(OUTPUT_DIR, "post_{:02}.png")

            output_file = save_to.format(frame_num)
            crop.save(output_file)

            images.append(output_file)
            frame_num += 1

    return images