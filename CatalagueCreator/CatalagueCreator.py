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

import rhinoscriptsyntax as rs
import scriptcontext as sc

def UpdateJsonFile(imageCollectionFolder, json_object):
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

def GetParamsDict(jewelName, jewelryImagePath, jewelryCADPath, CADVolume):
    paramDict = {"Jewel name" : jewelName, "image path" : jewelryImagePath, "cad path" : jewelryCADPath, "cad volume" : CADVolume}
    return paramDict

def FindCADFileFromJewelName(jewelName, CADCollectionFolderList):
    CADFile = ""
    ignoreKeys = ["DOC", "P", "S", "T", "F"]
    for CADCollectionFolder in CADCollectionFolderList:
        for path, subdirs, files in os.walk(CADCollectionFolder):
            for CADFile in files:
                if (CADFile.endswith(".3dm") or CADFile.endswith(".3DM")):
                    CADName = os.path.splitext(CADFile)[0]
                    jewelNameKeys = jewelName.split()
                    bAlKeys = True
                    for aKey in jewelNameKeys:
                        if aKey not in ignoreKeys:
                            if aKey in CADName:
                                bAlKeys = bAlKeys * True
                            else:
                                bAlKeys = bAlKeys * False                    
                    if bAlKeys:
                        CADFile = os.path.join(path, CADFile)
                        print(CADFile)
                        return CADFile
    return CADFile


def CreateCatalagueInfo(imageCollectionFolder, CADCollectionFolderList):
    # numberOfInputArgs = len(sys.argv)
    # imageCollectionFolder = sys.argv[1]
    # CADCollectionFolderList = []
    # for c in range (2,numberOfInputArgs):
    #     CADCollectionFolderList.append(sys.argv[c])

    # iterate over files in image collection folder
    for imageFilename in os.listdir(imageCollectionFolder):
        if (imageFilename.endswith(".png") or imageFilename.endswith(".jpg") or imageFilename.endswith(".jpeg")):
            filePath = os.path.join(imageCollectionFolder, imageFilename)
            # checking if it is a file
            if os.path.isfile(filePath):
                print "Image File :" + filePath
                
                # Find CAD file from image file
                jewelName = os.path.splitext(imageFilename)[0]
                CADFilePath = FindCADFileFromJewelName(jewelName, CADCollectionFolderList)
                CADVolume = 0.0
                if os.path.isfile(CADFilePath):
                    # Load CAD file
                    print "Cad File path :" + CADFilePath 
                    CADFolderPath = os.path.dirname(CADFilePath)
                    CADName = os.path.basename(CADFilePath)
                    strOpenCmd ='_-Open "' + CADFilePath +'"'
                    print "StrOpenCmd : "+strOpenCmd
                    bOpened = rs.Command('_-Open No '+'"'+CADFilePath+'"')
                    if not bOpened:
                        bOpened = rs.Command('_-Open '+'"'+CADFilePath+'"')
                    # rs.Command('_-Open "D:\\Work\\projects\\Jewelry\\CAD Files\\Just RIng\\", DR-5600.3dm')
                    # rs.Command('_-Insert "' + CADFilePath +'" Objects Enter 0,0,0 1 0')
                    # Compute volume
                    if bOpened:
                        CADVolume = 0.0
                        object_ids = rs.GetObjects("Select objects to compute volume")
                        for object_i in object_ids:
                            if object_i:
                                brep = rs.coercebrep(object_i)
                                if brep:
                                    blockVolume = brep.GetVolume()
                                    CADVolume = CADVolume + blockVolume
                    print CADVolume
                    
                # sc.doc.Objects.Clear()

                # Update Catalague info
                paramDict = GetParamsDict(jewelName, filePath, CADFilePath,CADVolume)
                json_object = json.dumps(paramDict, indent = 4)
                UpdateJsonFile(imageCollectionFolder, json_object)

# Defining main function
def main():
    CreateCatalagueInfo("D:\\Work\\projects\\Jewelry\\Catalague\\Ring Collection\\Color stone", ["D:\\Work\\projects\\Jewelry\\CAD Files\\Just RIng","D:\\Work\\projects\\Jewelry\\CAD Files\\Ladies Ring Collection"])
    
if __name__ == "__main__":
    main()