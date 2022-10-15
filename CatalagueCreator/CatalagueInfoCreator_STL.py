import json
import sys
import os
import glob

import vtk

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

def FindSTLFileFromJewelName(jewelName, CADCollectionFolderList):
    STLFile = ""
    ignoreKeys = ["DOC", "P", "S", "T", "F", "GP"]
    for CADCollectionFolder in CADCollectionFolderList:
        for path, subdirs, files in os.walk(CADCollectionFolder):
            for STLFile in files:
                if (STLFile.endswith(".stl") or STLFile.endswith(".STL")):
                    CADName = os.path.splitext(STLFile)[0]
                    jewelNameKeys = jewelName.split()
                    bAlKeys = True
                    for aKey in jewelNameKeys:
                        if aKey not in ignoreKeys:
                            if aKey == CADName:
                                bAlKeys = bAlKeys * True
                            else:
                                bAlKeys = bAlKeys * False                    
                    if bAlKeys:
                        STLFile = os.path.join(path, STLFile)
                        print(STLFile)
                        return STLFile
    return STLFile

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

def CreateCatalagueInfo_RingSTL(imageCollectionFolder, CADCollectionFolderList,designIdentifier):
    # iterate over files in image collection folder
    count = 1
    for imageFilename in os.listdir(imageCollectionFolder):
        if (imageFilename.endswith(".png") or imageFilename.endswith(".jpg") or imageFilename.endswith(".jpeg")):
            filePath = os.path.join(imageCollectionFolder, imageFilename)
            # checking if it is a file
            if os.path.isfile(filePath):
                print ("Image File :" + filePath)
                
                # Find CAD file from image file
                jewelName = os.path.splitext(imageFilename)[0]
                STLFilePath =  FindSTLFileFromJewelName(jewelName, CADCollectionFolderList)
                print ("STL File :" + STLFilePath)
                # bAddedBefore = IsAddedBefore(imageCollectionFolder, STLFilePath)
                bAddedBefore = False
                if os.path.isfile(STLFilePath) and not bAddedBefore:
                    # Load CAD file
                    print ("Cad File path :" + STLFilePath )
                    CADFolderPath = os.path.dirname(STLFilePath)
                    CADName = os.path.basename(STLFilePath)
                    
                    # Open STL file
                    reader = vtk.vtkSTLReader()
                    reader.SetFileName(STLFilePath)
                    reader.Update()
                    jewelPolyData = reader.GetOutput()
                    # print (jewelPolyData)

                    if jewelPolyData:
                        measured_polydata = vtk.vtkMassProperties()
                        measured_polydata.SetInputData(jewelPolyData)
                        fVolume = measured_polydata.GetVolume()
                        fVolume = fVolume/1000.0
                        print ("STL volume :", fVolume )
                        uniqueName = designIdentifier + str(count)
                        count = count + 1

                        # Update Catalague info
                        paramDict = GetParamsDict(uniqueName, jewelName, filePath, STLFilePath,fVolume, True, [False,False])
                        json_object = json.dumps(paramDict, indent = 4)
                        UpdateJsonFile(imageCollectionFolder, json_object)


# Defining main function
def main():
    # Inputs
    selected_images_folder_path = "D:/Work/projects/Jewelry/Catalague/Ring Collection/NokataRings"
    CAD_folder_path =  ["D:/Work/projects/Jewelry/CAD Files/JALI Ring"]
    designIdentifier = "NOK-"

    # Start Info creator
    CreateCatalagueInfo_RingSTL(selected_images_folder_path,CAD_folder_path,designIdentifier)
    
if __name__ == "__main__":
    main()