# Given folder with jewelry images
# respective CAD file is found 
# Check if CAD can be opened
# Estimate the mass of the jewelry in gms
# Check if can be resized with RingResizer of MatrixGold
# Create an unique ID 
# Create/Update json file with image name, CAD name, unique name, mass, can resize

# Run command
# python CatalagueCreator.py -imageCollection <folder_path> -CADCollection list[<folder_path>] 
import json
import sys
import os
import glob

def UpdateJsonFile(json_object):
    imageCollectionFolder = sys.argv[1]
    listObj = []

    jsonFilePath = os.path.join(imageCollectionFolder,"CatalagueInfo.json")
    if os.path.isfile(jsonFilePath):
        with open(jsonFilePath, 'r') as readfile:
            listObj = json.load(readfile)
            # print(listObj)
    
    z = json.loads(json_object)
    listObj.append(z)
    with open(jsonFilePath, 'w') as outfile:
        json.dump(listObj, outfile, indent = 3)

def GetParamsDict(jewelName, jewelryImagePath, jewelryCADPath):
    paramDict = {"image name" : jewelName, "image path" : jewelryImagePath, "cad path" : jewelryCADPath}
    return paramDict

def FindCADFileFromJewelName(jewelName, CADCollectionFolderList):
    CADFile = "Not Found"
    ignoreKeys = ["DOC", "P", "S", "T", "F"]
    for CADCollectionFolder in CADCollectionFolderList:
        for CADFilePath in glob.iglob(CADCollectionFolder + '**/**', recursive=True):
            if (CADFilePath.endswith(".3dm") or CADFilePath.endswith(".3DM")):
                CADName = os.path.splitext(CADFilePath)[0]
                jewelNameKeys = jewelName.split()
                bAlKeys = True
                for aKey in jewelNameKeys:
                    if aKey not in ignoreKeys:
                        if aKey in CADName:
                            bAlKeys = bAlKeys * True
                        else:
                            bAlKeys = bAlKeys * False                    
                if bAlKeys:
                    CADFile = os.path.join(CADCollectionFolder, CADFilePath)
                    print(CADFile)
                    return CADFile
    
    print(CADFile)
    return CADFile


def CreateJsonFile():
    numberOfInputArgs = len(sys.argv)
    imageCollectionFolder = sys.argv[1]
    CADCollectionFolderList = []
    for c in range (2,numberOfInputArgs):
        CADCollectionFolderList.append(sys.argv[c])

    # iterate over files in image collection folder
    for imageFilename in os.listdir(imageCollectionFolder):
        if (imageFilename.endswith(".png") or imageFilename.endswith(".jpg") or imageFilename.endswith(".jpeg")):
            filePath = os.path.join(imageCollectionFolder, imageFilename)
            # checking if it is a file
            if os.path.isfile(filePath):
                # print(filePath)
                jewelName = os.path.splitext(imageFilename)[0]
                CADFilePath = FindCADFileFromJewelName(jewelName, CADCollectionFolderList)
                paramDict = GetParamsDict(jewelName, filePath, CADFilePath)
                # print(paramDict)
                # Serializing json
                json_object = json.dumps(paramDict, indent = 4)
                UpdateJsonFile(json_object)

# Defining main function
def main():
    CreateJsonFile()
    
if __name__ == "__main__":
    main()