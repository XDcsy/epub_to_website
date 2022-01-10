import sys
import ntpath
import os
from zipfile import ZipFile
from xml.dom import minidom
from xml.etree import ElementTree as ET
import configparser
from shutil import copy

# a directory in the .epub file is valid(needed) when:
# it is toc.ncx file OR it is /OEBPS/{validDirTypes}
def isValidDir(pathTuple, validDirTypes, TOC):
    if pathTuple[0].endswith(validDirTypes):
        return True
    elif pathTuple[1] == TOC:
        return True
    else:
        return False

# generate filenames without the /OEBPS directory structure
def toTargetName(pathTuple, TOC):
    if pathTuple[1] == TOC:
        return pathTuple[1]
    else:
        d = ntpath.basename(pathTuple[0])
        f = pathTuple[1]
        return ntpath.join(d, f)
    
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def generateTitle(docTitle):
    titleName = docTitle[0].getElementsByTagName("text")[0]
    return getText(titleName.childNodes)
    
def generateDate(p):
    for pNode in p:
        if pNode.getAttribute("class") == "date":
            return getText(pNode.childNodes)
    return ""
    
def generatePreview(p, previewMaxLen):
    for pNode in p:
        if pNode.getAttribute("class") != "date":
            preview = getText(pNode.childNodes)
            if len(preview) > previewMaxLen:
                preview = preview[:previewMaxLen] + "  ......"
            return preview
    return ""
    
def generateTag(meta):
    for mNode in meta:
        if mNode.getAttribute("name") == "keywords":
            return mNode.getAttribute("content")
    return ""
    
    
def getPageName(navLabel):
    pageName = navLabel[0].getElementsByTagName("text")[0]
    return getText(pageName.childNodes)
        
def getPageSrc(content):
    pageSrc = content[0].getAttribute("src")
    return pageSrc

def generatePages(navPoint):
    pages = []
    for p in navPoint:
        navLabel = p.getElementsByTagName("navLabel")
        content = p.getElementsByTagName("content")
        pages.append((getPageSrc(content), getPageName(navLabel)))
    return pages

def addPageCSS():
    return
    
def epubToWebsite(inputFilePath,\
                    validDirTypes = ("Images", "Styles", "Text"),\
                    OEBPS = "OEBPS",\
                    TOC = "toc.ncx",\
                    epubEncoding = "utf-8",\
                    indexCSS = "index.css",\
                    pageCSS = "",\
                    newFolder = False,\
                    withTime = False,\
                    withPreview = False,\
                    withTag = False,\
                    reversedOrder = False,\
                    previewMaxLen = 300):
                    
    fileName = ntpath.basename(inputFilePath)
    if not fileName.endswith(".epub"):
        print("File format not supported")
    
    else:
        if newFolder:
            outputDir = fileName.replace(".epub", "") + "/"
        else:
            outputDir = "./"
    
        with ZipFile(inputFilePath, 'r') as zipObj:
           zipInfo = zipObj.infolist()
           for info in zipInfo:
                if info.filename.startswith(OEBPS):
                    # unzip without keeping the /OEBPS directory
                    pathTuple = ntpath.split(info.filename)
                    if isValidDir(pathTuple, validDirTypes, TOC):
                       info.filename = toTargetName(pathTuple, TOC)
                       zipObj.extract(info, outputDir)
    
    # now all the files are extracted
    # we need to convert the table of contents file (toc.ncx)
    # to an index.html

    if os.path.isfile(ntpath.join(outputDir, TOC)):
        with minidom.parse(ntpath.join(outputDir, TOC)) as dom:
            titleContent = generateTitle(dom.getElementsByTagName("docTitle"))
            pageContent = generatePages(dom.getElementsByTagName("navPoint"))
    
            html = ET.Element('html')
            head = ET.Element('head')
            meta = ET.Element('meta', attrib={'http-equiv': "Content-Type", "content":"text/html;charset=utf-8"})
            title = ET.Element('title')
            title.text = titleContent
            style = ET.Element('link', attrib={'rel':'stylesheet', 'href':indexCSS})
            body = ET.Element('body')
            container_div = ET.Element('div', attrib={'class': "container-div"})
            tag_div = ET.Element('div')
            h1 = ET.Element('h1')
            h1.text = titleContent
            head.append(meta)
            head.append(title)
            head.append(style)
            container_div.append(h1)
            if withTag:
                container_div.append(tag_div)
            html.append(head)
            body.append(container_div)
            html.append(body)
            
            if reversedOrder:
                pageContent = reversed(pageContent)
            
            tags = []
            for p in pageContent:
                a = ET.Element('a', attrib={'href': p[0], 'class': "link-a"})
                div = ET.Element('div', attrib={'class': "link-div"})
                pHeadlineNode = ET.Element('p', attrib={'class': "headline"})
                pHeadlineNode.text = p[1]
                div.append(pHeadlineNode)
                a.append(div)
                
                # if any of the conditions blow is True, we need to parse the html pages in the epub
                xhtmlFile = outputDir + p[0]
                if withTime or withPreview or withTag:
                    with minidom.parse(xhtmlFile) as fdom:
                        if withPreview:
                            preview = generatePreview(fdom.getElementsByTagName("p"), previewMaxLen)
                            if len(preview) > 0:
                                pPreviewNode = ET.Element('p', attrib={'class': "preview"})
                                pPreviewNode.text = preview
                                div.append(pPreviewNode)
                        if withTime:
                            date = generateDate(fdom.getElementsByTagName("p"))
                            if len(date) > 0:
                                pDateNode = ET.Element('p', attrib={'class': "date"})
                                pDateNode.text = date
                                div.append(pDateNode)
                        if withTag:
                            tag = generateTag(fdom.getElementsByTagName("meta"))
                            if len(tag) > 0:
                                a.set("data-tag", tag)
                                tags.extend([t.strip() for t in tag.split(',')])
                container_div.append(a)

                # if pageCSS is not empty, we need to add one <link> tag to the html pages
                if len(pageCSS) > 0:
                    # pageCSS is accessed from within ./Text
                    innerPageCSS = "../" + pageCSS
                    with open(xhtmlFile, 'r+', encoding=epubEncoding) as f:
                        # add it directly after the <head> tag
                        fileContent = f.read()
                        link = '<link rel="stylesheet" href="'+innerPageCSS+'"></link>'
                        fileContent = fileContent.replace("<head>","<head>"+link,1)
                        # overwirte
                        f.seek(0)
                        f.write(fileContent)
                        f.truncate()
            
            if withTag:
                from collections import Counter
                tagCounter = Counter(tags)
                tagsSort = tagCounter.most_common()
                allBtn = ET.Element('button', attrib={'class': "tag", "id": "All"})
                allBtn.text = "ALL"+" (" + str(len(tags)) + ")"
                tag_div.append(allBtn)
                for (tag, freq) in tagsSort:
                    tagBtn = ET.Element('button', attrib={'class': "tag", "id": tag})
                    tagBtn.text = tag+" (" + str(freq) + ")"
                    tag_div.append(tagBtn)
                    
                js = ET.Element('script', attrib={'src':'index.js'})
                html.append(js)
                
            ET.ElementTree(html).write(open(ntpath.join(outputDir, 'index.html'), 'wb'), encoding='utf-8',
                             method='html')

            # if the epub is extracted to a new folder, we need to copy js and css files to the new path
            if newFolder:
                copy("index.js", outputDir)
                copy(indexCSS, outputDir)
                copy(pageCSS, outputDir)



    else:
        print("please add toc.ncx fallback to epub3")

if __name__ == '__main__':
    # read run.properties file
    config = configparser.ConfigParser()
    config.read('run.properties')
    newFolder = int(config['configs']['newFolder'])
    withTime = int(config['configs']['withTime'])
    withPreview = int(config['configs']['withPreview'])
    previewMaxLen = int(config['configs']['previewMaxLen'])
    withTag = int(config['configs']['withTag'])
    reversedOrder = int(config['configs']['reversedOrder'])
    epubEncoding = config['configs']['epubEncoding']
    indexCSS = config['configs']['indexCSS']

    if config.has_option('optional', 'pageCSS'):
        pageCSS = config['optional']['pageCSS']
    else:
        pageCSS = ""

    # built-in properties
    validDirTypes = ("Images", "Styles", "Text")
    OEBPS = "OEBPS"
    TOC = "toc.ncx"

    # inputFilePath = "test.epub"
    inputFilePath = sys.argv[1]
    epubToWebsite(inputFilePath, validDirTypes, OEBPS, TOC, epubEncoding, indexCSS, pageCSS, newFolder, withTime, withPreview, withTag, reversedOrder, previewMaxLen)
