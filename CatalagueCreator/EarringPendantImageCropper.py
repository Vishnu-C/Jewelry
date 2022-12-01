# Given sepereate images of earring pair and pendant, below implementation creates a combined image with design name

import cv2
import os
import pathlib
import numpy as np

# I. Crop to remove all black rows and columns across entire image
def crop_image(img):
    mask = img!=255
    mask = mask.any(2)
    mask0,mask1 = mask.any(0),mask.any(1)
    return img[np.ix_(mask1,mask0)]

# II. Crop while keeping the inner all black rows or columns
def crop_image_v2(img):
    mask = img!=255
    mask = mask.any(2)
    mask0,mask1 = mask.any(0),mask.any(1)
    colstart, colend = mask0.argmax(), len(mask0)-mask0[::-1].argmax()+1
    rowstart, rowend = mask1.argmax(), len(mask1)-mask1[::-1].argmax()+1
    return img[rowstart:rowend, colstart:colend, :]

def VerticalSplitImage(img):

    h, w, channels = img.shape
    
    half = w//2    
    
    # this will be the first column
    left_part = img[:, :half,:] 
    
    # [:,:half] means all the rows and
    # all the columns upto index half
    
    # this will be the second column
    right_part = img[:, half:,:]  

    return left_part, right_part

def CropToContents(image_file_path):
    # read image
    img = cv2.imread(image_file_path)

    # crop image
    croppedImg = crop_image_v2(img)

    # save cropped file
    fileNameWithoutExt = pathlib.Path(image_file_path).stem
    fileExtension = pathlib.Path(image_file_path).suffix
    folderPath = pathlib.Path(image_file_path).parent
    # new file name
    cropped_fileName = fileNameWithoutExt+ '_Cropped'
    output_path = pathlib.PurePath(folderPath, cropped_fileName + fileExtension)
    # print("Cropped image path :", str(output_path))
    # cv2.imwrite(str(output_path), croppedImg)

    return croppedImg

# Can be used for spliting earrings images
def CropToContentsAndVerticalSplit(image_file_path):
    # read image
    img = cv2.imread(image_file_path)

    # crop image
    croppedImg = crop_image_v2(img)

    # Vertical split image
    leftPart, rightPart = VerticalSplitImage(img)

    # crop again after split
    leftPart = crop_image_v2(leftPart)
    rightPart = crop_image_v2(rightPart)

    # save split images
    fileNameWithoutExt = pathlib.Path(image_file_path).stem
    fileExtension = pathlib.Path(image_file_path).suffix
    folderPath = pathlib.Path(image_file_path).parent
    # left file name
    left_fileName = fileNameWithoutExt+ '_left'
    leftImagepath = pathlib.PurePath(folderPath, left_fileName + fileExtension)
    # cv2.imwrite(str(leftImagepath), leftPart)
    # right file name
    right_fileName = fileNameWithoutExt+ '_right'
    rightImagepath = pathlib.PurePath(folderPath, right_fileName + fileExtension)
    # cv2.imwrite(str(rightImagepath), rightPart)

    return leftPart, rightPart

# Defining main function
def main():
    # Inputs
    selected_images_folder_path = "D:/Work/projects/Jewelry/Catalague/PendantEarRing/Fancy"

    jewelList = []
    for imageFilename in os.listdir(selected_images_folder_path):
        if (imageFilename.endswith(".png") or imageFilename.endswith(".jpg") or imageFilename.endswith(".jpeg")):
            strJewelDesignID = ""
            for d in imageFilename:
                if d.isdigit():
                    strJewelDesignID = strJewelDesignID + d
            print (strJewelDesignID)
            penErrInfo = {"jewelDesignID" : strJewelDesignID, "folderPath" : None, "Pendant" : None, "EarringLeft" : None, "EarringRight" : None }
            bPreset = False
            for aJewel in  jewelList:
                aJewelId =  aJewel["jewelDesignID"]
                if aJewelId.__contains__(str(strJewelDesignID)):
                    penErrInfo = aJewel
                    bPreset = True

            image_file_path = os.path.join(selected_images_folder_path, imageFilename)
            if imageFilename.__contains__("EP") or imageFilename.__contains__("ET") :
                errLeft, errRight = CropToContentsAndVerticalSplit(image_file_path)
                penErrInfo ["EarringLeft"] = errLeft
                penErrInfo ["EarringRight"] = errRight
            else:
                pendant = CropToContents(image_file_path)
                penErrInfo ["Pendant"] = pendant
            
            folderPath = pathlib.Path(image_file_path).parent
            penErrInfo["folderPath"] = folderPath

            if not bPreset:
                jewelList.append(penErrInfo)

    for aJewel in  jewelList:
        imgLen = 3000
        imbHeight = 5000
        l_img = np.zeros((imgLen,imbHeight,3), np.uint8)
        l_img.fill(255)

        s_img = aJewel["EarringLeft"]
        hERSize = 1500
        wERSize = round((s_img.shape[1]/s_img.shape[0]) * hERSize)
        dim = (wERSize, hERSize)
        # resize image
        s_img = cv2.resize(s_img, dsize=dim, interpolation = cv2.INTER_AREA)
        x_offset=y_offset=50
        y1, y2 = y_offset, y_offset + s_img.shape[0]
        x1, x2 = x_offset, x_offset + s_img.shape[1]
        l_img[y1:y2, x1:x2] = (s_img[:, :] )
            
        s_img = aJewel["Pendant"]
        x_offset = x2
        y1, y2 = y_offset, y_offset + s_img.shape[0]
        x1, x2 = x_offset, x_offset + s_img.shape[1]
        for c in range(0, 3):
            l_img[y1:y2, x1:x2, c] = (s_img[:, :, c] )

        s_img = aJewel["EarringRight"]
        # resize image
        s_img = cv2.resize(s_img, dsize=dim, interpolation = cv2.INTER_AREA)
        x_offset = x2
        y1, y2 = y_offset, y_offset + s_img.shape[0]
        x1, x2 = x_offset, x_offset + s_img.shape[1]
        l_img[y1:y2, x1:x2] = (s_img[:, :] )

        # crop image to contents
        l_img = crop_image_v2(l_img)
        # final resize
        wSize = 1500
        hSize = round((l_img.shape[0]/l_img.shape[1]) * wSize)
        dim = (wSize, hSize)
        # resize image
        l_img = cv2.resize(l_img, dsize=dim, interpolation = cv2.INTER_AREA)

        outFile = str(aJewel["folderPath"])+"//"+aJewel["jewelDesignID"]+".jpg"
        # print(outFile)
        # cv2.imwrite(str(outFile), l_img)

        # fit image
        imageWidth = 1500
        imageHeight = 2000
        fitImg = np.zeros((imageHeight,imageWidth,3), np.uint8)
        fitImg.fill(255)
        heightOffset = round(abs(imageHeight - l_img.shape[0]) * 0.5)
        print("heightOffset ", heightOffset)
        y1, y2 = heightOffset ,heightOffset + l_img.shape[0]
        x1, x2 = 0,l_img.shape[1]
        fitImg[y1:y2, x1:x2] = (l_img[:, :] )

        print(outFile)
        cv2.imwrite(str(outFile), fitImg)

if __name__ == "__main__":
    main()