import sys
import ntpath
import os
from zipfile import ZipFile
from xml.dom import minidom
from xml.etree import ElementTree as ET

validDirTypes = ("Images", "Styles", "Text")
OEBPS = "OEBPS"
TOC = "toc.ncx"
TOC_ENCODING = "UTF-8"
CSS = ".container-div {width: 800px;margin: 0 auto}.link-div {margin-top:15px; margin-bottom:15px; margin-left:20px}a{text-decoration:none;}a:link,a:visited{text-decoration:none;}"

# a directory in the .epub file is valid(needed) when:
# it is toc.ncx file OR it is /OEBPS/{validDirTypes}
def isValidDir(pathTuple):
    if pathTuple[0].endswith(validDirTypes):
        return True
    elif pathTuple[1] == TOC:
        return True
    else:
        return False


# generate filenames without the /OEBPS directory structure
def toTargetName(pathTuple):
    if pathTuple[1] == TOC:
        return pathTuple[1]
    else:
        d = ntpath.basename(pathTuple[0])
        f = pathTuple[1]
        return ntpath.join(d, f)
    
inputFilePath = sys.argv[1]
fileName = ntpath.basename(inputFilePath)

if not fileName.endswith(".epub"):
    print("File format not supported")
    
else:
    outputDir = "./"
    # outputDir = fileName.replace(".epub", "")
    

    with ZipFile(inputFilePath, 'r') as zipObj:
       zipInfo = zipObj.infolist()
       for info in zipInfo:
            if info.filename.startswith(OEBPS):
                # unzip without keeping the /OEBPS directory
                pathTuple = ntpath.split(info.filename)
                if isValidDir(pathTuple):
                   info.filename = toTargetName(pathTuple)
                   zipObj.extract(info, outputDir)
            
# now all the files are extracted
# we need to convert the table of contents file (toc.ncx)
# to an index.html

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def generateTitle(docTitle):
    titleName = docTitle[0].getElementsByTagName("text")[0]
    return getText(titleName.childNodes)
    
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
        h1 = ET.Element('h1')
        h1.text = titleContent
        head.append(meta)
        head.append(title)
        head.append(style)
        container_div.append(h1)
        html.append(head)
        body.append(container_div)
        html.append(body)
        for p in pageContent:
            div = ET.Element('div', attrib={'class': "link-div"})
            a = ET.Element('a', attrib={'href': p[0]})
            a.text = p[1]
            div.append(a)
            container_div.append(div)
    
        ET.ElementTree(html).write(open(ntpath.join(outputDir, 'index.html'), 'wb'), encoding='utf-8',
                             method='html')

else:
    print("please add toc.ncx fallback to epub3")



    