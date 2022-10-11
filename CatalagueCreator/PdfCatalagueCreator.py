import os
import json

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, Spacer, Image
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import red, yellow, blue, skyblue,steelblue

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


densityGold22K = 15.6 #g/cm3
fTableWidth = 4.5

def AllPageSetup(canvas, doc):

    canvas.saveState()

    p = canvas.beginPath()
    p.rect (0,0 , 21.0*cm , 29.7*cm)
    canvas.clipPath (p, stroke=0)
    canvas.linearGradient (0,0 , 21.0*cm , 29.7*cm, (skyblue, steelblue))    
    
    #footers
    pdfmetrics.registerFont(TTFont('Times', 'times.ttf',))
    canvas.setFont('Times', 15)
    canvas.drawRightString(10.5 * cm, 0.5 * cm, 'Page %d' % (doc.page))
    canvas.drawString(15.0 * cm, 1.0 * cm, 'Contact : Ukesh')
    canvas.drawString(15.0 * cm, 0.5 * cm, 'Mobile : +91 9629933184')


    pdfmetrics.registerFont(TTFont('JewelFont',"D:\Work\projects\Jewelry\Catalague\LmsSolitaryStone-r4O8.ttf"))
    canvas.setFillColorRGB(1.0, 0.84, 0.0) # gold
    canvas.setFont('JewelFont', 55)
    #header
    canvas.drawRightString(20.0 * cm, 27 * cm, "COLOR STONE")
    # canvas.drawRightString(10.5 * cm, 29 * cm, "doc.report_info")

    canvas.restoreState()

def CreateReportLabPDF(jewelInfos, pdfFilePath, fImageDimension):
    # container for the "Flowable" objects
    elements = []
    styles=getSampleStyleSheet()
    styleN = styles["Normal"]

    imagesNameList = []
    for aJewelInfo in jewelInfos:
        imagesNameList.append(aJewelInfo[0])

    # imagesFolderPath = "D:\\Work\\projects\\Jewelry\\Catalague\\Ring Collection\\Color stone"
    # for x in os.listdir(imagesFolderPath):
    #     if x.endswith(".jpg"):
    #         imagesNameList.append(imagesFolderPath+"\\"+x)

    data = [[]]
    for i in range(0,len(jewelInfos),4):
        # Images
        imagesList = []
        # design names
        designList = []
        for ii in range (0,4):
            if(i+ii < len(jewelInfos)):
                aJewelInfo = jewelInfos[i+ii]
                im = Image(aJewelInfo[0], fImageDimension[0]*cm, fImageDimension[1]*cm)
                imagesList.append(im)
                designWeight = aJewelInfo[1]
                strDesignWeight = "{:.3f}".format(designWeight)
                designName = aJewelInfo[2]
                # print (i+ii, ii, designName)
                designList.append(designName+" : "+strDesignWeight+" gm")
        data.append(imagesList)
        data.append(designList)

    tableThatSplitsOverPages = Table(data, [fTableWidth * cm, fTableWidth * cm, fTableWidth * cm, fTableWidth * cm], repeatRows=1)
    tblStyle = TableStyle([('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN',(0,0),(-1,-1),'TOP')
                        ])
    # tblStyle.add('BACKGROUND',(0,0),(1,0),colors.lightblue)
    tblStyle.add('BACKGROUND',(0,1),(-1,-1),colors.white)
    tableThatSplitsOverPages.setStyle(tblStyle)
    elements.append(tableThatSplitsOverPages)

    # pdfReportPages = "./Catalague_ColorStone.pdf"
    doc = SimpleDocTemplate(pdfFilePath, pagesize=A4)
    doc.build(elements, onFirstPage=AllPageSetup, onLaterPages=AllPageSetup)

def GetJewelInfo(catalagueInfoJsonFile):
    jewelInfos = []
    if os.path.isfile(catalagueInfoJsonFile):
        with open(catalagueInfoJsonFile, 'r') as readfile:
            infoListObj = json.load(readfile)
            for aInfo in infoListObj:
                fVolume = aInfo["cad volume"] #cm3
                if fVolume > 0.0:
                    strImagePath = ""
                    bRingResize = aInfo["ring resizable"]
                    if bRingResize:
                        strImagePath = aInfo["image path"]
                    else:
                        bUngroupable = aInfo["ring ungroupable"]
                        if bUngroupable:
                            strImagePath = aInfo["image path"]
                    if len(strImagePath) > 0:
                        mass = densityGold22K * fVolume
                        strUniqueName = aInfo["Unique name"]
                        aJewelInfo = [strImagePath,mass,strUniqueName]
                        jewelInfos.append(aJewelInfo)

    return jewelInfos

def main():
    # Input
    catalagueInfoJsonFile = "D:\Work\projects\Jewelry\Catalague\Ring Collection\Color stone\CatalagueInfo.json"
    pdfOutputFile = "D:\Work\projects\Jewelry\Catalague\Ring Collection\Color stone\Catalague_ColorStone.pdf"
    fImageDimension = [4.0,3.0]

    jewelInfos = GetJewelInfo(catalagueInfoJsonFile)
    print (jewelInfos)
    CreateReportLabPDF(jewelInfos, pdfOutputFile,fImageDimension)

if __name__ == "__main__":
    main()