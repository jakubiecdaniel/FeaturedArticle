from PIL import Image
import cv2
import os
import sys

def PNGtoJPG(image_path,image_new_path):


    png_img = cv2.imread(image_path)


    cv2.imwrite(image_new_path, png_img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    return image_new_path

def resize(image_path):

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    width = 800
    height = 800

    dim = (width,height)
    resized = cv2.resize(img,dim, interpolation=cv2.INTER_AREA)

    #image_new_path = "sc2.jpg"

    cv2.imwrite(image_path,resized)

    return image_path
    #return image_new_path

def SplitAndCrop(image_path):
    images = []

    filename = image_path
    img = Image.open(filename)
    width, height = img.size
    start_pos = start_x, start_y = (0, 0)
    cropped_image_size = w, h = (width,int(height/10)) #800

    frame_num = 1
    for col_i in range(0, width, w):
        for row_i in range(0, height, h):
            crop = img.crop((col_i, row_i, col_i + w, row_i + h))
            save_to= os.path.join("./output", "post_{:02}.png")

            output_file = save_to.format(frame_num)
            crop.save(output_file)
            resize(output_file)

            images.append(output_file)
            frame_num += 1

    return images

