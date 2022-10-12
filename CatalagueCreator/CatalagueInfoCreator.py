#########
# Creates Catalauge info as json file, which is used for creating pdf catalague
# Author - Vishnu C
#########

###### Prerequest
# A manual selection of images is done and kept in a individual folder 

###### Run Info
# Run in EditPythonScript window of MatrixGold
 
# Selected images for catalgue creation <selected_images_folder_path>, the folder paths of all the respective CAD files to be searched are listed in [<CAD_folder_path>] 

##### Process performed
# Given folder with jewelry images
# respective CAD file is found 
# Check if CAD can be opened
# Estimate the volume of the jewelry in m3
# Check if can be resized with RingResizer of MatrixGold
# Check if can be ungrouped so that can resize with RingResizer of RhinoGold
# Create an unique ID 
# Create/Update json file with image name, CAD name, unique name, volume and various checks

import json
import sys
import os
import glob

import rhinoscriptsyntax as rs

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

def GetParamsDict(uniqueName, jewelName, jewelryImagePath, jewelryCADPath, CADVolume, bRingResize, bQuries):
    paramDict = {"Unique name" : uniqueName, "Jewel name" : jewelName, "image path" : jewelryImagePath, "cad path" : jewelryCADPath, "cad volume" : CADVolume, "ring resizable" : bRingResize, "ring ungroupable" : bQuries[0], "Large stone missing" : bQuries[1]}
    return paramDict

def FindCADFileFromJewelName(jewelName, CADCollectionFolderList):
    CADFile = ""
    ignoreKeys = ["DOC", "P", "S", "T", "F", "GP"]
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

def IsAddedBefore(imageCollectionFolder, CADFilePath):
    jsonFilePath = os.path.join(imageCollectionFolder,"CatalagueInfo.json")
    if os.path.isfile(jsonFilePath):
        with open(jsonFilePath, 'r') as readfile:
            infoListObj = json.load(readfile)
            for aInfo in infoListObj:
                strCADPath = aInfo["cad path"]
                if strCADPath == CADFilePath:
                    return True
    return False

def CreateCatalagueInfo(imageCollectionFolder, CADCollectionFolderList,designIdentifier):
    # iterate over files in image collection folder
    count = 1
    for imageFilename in os.listdir(imageCollectionFolder):
        if (imageFilename.endswith(".png") or imageFilename.endswith(".jpg") or imageFilename.endswith(".jpeg")):
            filePath = os.path.join(imageCollectionFolder, imageFilename)
            # checking if it is a file
            if os.path.isfile(filePath):
                print "Image File :" + filePath
                
                # Find CAD file from image file
                jewelName = os.path.splitext(imageFilename)[0]
                CADFilePath = FindCADFileFromJewelName(jewelName, CADCollectionFolderList)
                bAddedBefore = IsAddedBefore(imageCollectionFolder, CADFilePath)
                if os.path.isfile(CADFilePath) and not bAddedBefore:
                    # Load CAD file
                    print "Cad File path :" + CADFilePath 
                    CADFolderPath = os.path.dirname(CADFilePath)
                    CADName = os.path.basename(CADFilePath)
                    
                    # Open 3DM file
                    bOpened = rs.Command('_-Open No '+'"'+CADFilePath+'"')
                    if not bOpened:
                        bOpened = rs.Command('_-Open '+'"'+CADFilePath+'"')

                    # rs.Command('_-Open "D:\\Work\\projects\\Jewelry\\CAD Files\\Just RIng\\", DR-5600.3dm')
                    # rs.Command('_-Insert "' + CADFilePath +'" Objects Enter 0,0,0 1 0')

                    # Check if ring resizer works 
                    # Compute volume
                    if bOpened:
                        CADVolume = 0.0
                        bRingResize = [False]
                        items = ("RingResizer", "No", "Yes")
                        bRingResize = rs.GetBoolean("Check queries", items, (False) )
                        rs.Command("-Ungroup")
                        object_ids = rs.GetObjects("Select objects to compute volume")
                        if object_ids :
                            for object_i in object_ids:
                                if object_i:
                                    brep = rs.coercebrep(object_i)
                                    if brep:
                                        blockVolume = brep.GetVolume()
                                        CADVolume = CADVolume + blockVolume
                                        # print CADVolume
                                        # print "results :", results 
                                        
                        # Convert to centimeter 
                        cenimeter_system = 3 # https://developer.rhino3d.com/api/RhinoScriptSyntax/#document-UnitSystem
                        fScaleFactor = rs.UnitScale(cenimeter_system)
                        CADVolume = fScaleFactor**3 * CADVolume
                        items = ("CanUngroup", "No", "Yes"),("LargeStoneMissing","No","Yes")
                        bQuries = rs.GetBoolean("Check queries", items, (False,False) )
                        if bRingResize is None:
                            bRingResize = rs.GetBoolean("Check queries", items, (False) )
                        if bQuries is None:
                            bQuries = rs.GetBoolean("Check queries", items, (False,False) )

                        uniqueName = designIdentifier + str(count)
                        count = count + 1

                        # Update Catalague info
                        paramDict = GetParamsDict(uniqueName, jewelName, filePath, CADFilePath,CADVolume,bRingResize[0], bQuries)
                        json_object = json.dumps(paramDict, indent = 4)
                        UpdateJsonFile(imageCollectionFolder, json_object)

# Defining main function
def main():
    # Inputs
    selected_images_folder_path = "D:/Work/projects/Jewelry/Catalague/Ring Collection/Floral"
    CAD_folder_path =  ["D:/Work/projects/Jewelry/CAD Files/Just RIng","D:/Work/projects/Jewelry/CAD Files/Ladies Ring Collection"]
    designIdentifier = "FL"

    # Start Info creator
    CreateCatalagueInfo(selected_images_folder_path,CAD_folder_path,designIdentifier)
    
if __name__ == "__main__":
    main()