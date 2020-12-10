# epub_to_website
 
## What is this
It's a simple script that unpacks an epub ebook to a website-like sturcture, which can then be directly uploaded and hosted at places like GitHub pages.

Example: https://xdcsy.github.io/

## How to use
Get `epub_to_website.exe` at the release page, and just drag and drop your epub file to the exe.

An index page will be automatically generated. The page title will be the same as your epub title.

If you are using GitHub pages, simply upload everything unpacked to your github.io repo, and it should work.

### Some optional functions

In your epub, if you have `<p class = "date"></p>` in the xhtml files, the dates will be displayed at the index page. The first `<p></p>` which is not `"date"` class will be previewed on the index page.

In your epub, you can specify the tags of an xhtml by placing a meta tag with `name="keywords"`, e.g.
``` XHTML
<meta name="keywords" content="Scala, Java, BigData" />
```
If you choose to display tags, make sure to include the index.js file. Otherwise you don't need the js file.


You can also call this tool in Python:

``` Python3
from epub_to_website import epubToWebsite
epubToWebsite(inputFilePath = "path/to/epub/file",\
              CSS = "body {width: 1200px} ...",\
              newFolder = True,\
              withTime = True,\
              withPreview = True,\
			  withTag = True,\
              reversedOrder = True,\
              previewMaxLen = 300)

# CSS:
#     Your custom CSS to use for generating index.html
#
# newFolder:
#     Unpack to the current directory or create a new folder.
#     If True, folder name will be the title of the epub.
#
# withTime:
#     Display date on index page (if avaliable)
#
# withPreview:
#     Display article previews on index page
#
# withTag:
#     Display tags on index page
#
# reversedOrder:
#     Display articles in reversed order. Suitable for blogs
#
# previewMaxLen:
#     Max number of characters displayed in each preview 
```
