import sys
import ntpath
import os
from zipfile import ZipFile
from xml.dom import minidom
from xml.etree import ElementTree as ET

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
    
def epubToWebsite(inputFilePath,\
                    validDirTypes = ("Images", "Styles", "Text"),\
                    OEBPS = "OEBPS",\
                    TOC = "toc.ncx",\
                    TOC_ENCODING = "UTF-8",\
                    CSS = "",\
                    newFolder = False,\
                    withTime = False,\
                    withPreview = False,\
                    reversedOrder = False,\
                    withTag = False,\
                    previewMaxLen = 300):
                    
    fileName = ntpath.basename(inputFilePath)
    if not fileName.endswith(".epub"):
        print("File format not supported")
    
    else:
        if newFolder:
            outputDir = fileName.replace(".epub", "")
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
            style = ET.Element('style')
            style.text = CSS
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
            pageURLs = []
            
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
                
                if withTime or withPreview or withTag:
                    with minidom.parse(p[0]) as fdom:
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

    else:
        print("please add toc.ncx fallback to epub3")

if __name__ == '__main__':
    validDirTypes = ("Images", "Styles", "Text")
    OEBPS = "OEBPS"
    TOC = "toc.ncx"
    TOC_ENCODING = "UTF-8"
    CSS = "html{font-size:24px;background-color:#f3f3f3}h1{font-size:2em;margin-top:30px;}.container-div{margin:0 auto;margin-bottom:4em}@media(min-width:576px){html{font-size:30px;}.container-div{width:95%;}}@media(min-width:768px){html{font-size:30px;}.container-div{width:95%;}}@media(min-width:992px){html{font-size:20px;}.container-div{width:70%;}}@media(min-width:1200px){html{font-size:16px;}.container-div{width:70%;}}.link-div{background-color:white;color:black;margin-top:15px;margin-bottom:15px;margin-bottom:20px;border-radius:5px;box-shadow:1px 1px 5px 0 rgba(0,0,0,0.02), 1px 1px 15px 0 rgba(0,0,0,0.03);transition:transform 0.3s, background-color 0.3s, box-shadow 0.6s;transition-property:transform, background-color, box-shadow;transition-duration:0.3s, 0.3s, 0.6s;transition-timing-function:ease, ease, ease;transition-delay:0s, 0s, 0s;padding:10px;}.link-div:hover{transform: translateY(-5px);box-shadow: 1px 10px 30px 0 rgba(0,0,0,0.2);}a{text-decoration:none;}a:link,a:visited{text-decoration:none;}.headline{font-size:1.3em;font-weight: 450;line-height: 1.125;color:black;}.date{font-size:0.8em;color:gray;}.preview{color:#50596c}button.tag{margin: 0.35em;font-size: 1em;background-color: #f4f4f4;padding: 0.25rem 0.6rem 0.25rem 0.6rem;border-radius: 5px;border: 1px solid #6c757d;transition-duration: 0.4s;outline:none;}button.tag:hover{cursor:pointer;background-color:#6c757d !important;color:white !important;}"

    inputFilePath = sys.argv[1]
    epubToWebsite(inputFilePath, validDirTypes, OEBPS, TOC, TOC_ENCODING, CSS, newFolder = False, withTime = True, withPreview = True, withTag = True, reversedOrder = True, previewMaxLen = 300)
