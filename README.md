# epub_to_website
 
## Feature
It unpacks an epub ebook to a website-like sturcture with an auto-generated index page, which can then be directly opened (and hosted) as a website.

You may use it to host epub books on the Internet. For example (my blog): https://xdcsy.github.io/

Or you may just open the index page locally, and your browser can then be used as an epub reader.

## How to use
Get `epub_to_website.exe` at the release page, and just drag and drop your epub file to the exe.

An index page will be automatically generated. The title of the page will be the same as your epub title.

If you wish to host the epub as an website (e.g. at GitHub Pages), simply upload everything generated to your github.io repo, and it should work.

## Some extra functions

There are some extra functions mainly designed to display better index pages for notes and blogs (e.g. support for displaying dates, tags, preview ...)

### Display dates

In your epub, if you have `<p class = "date"></p>` in the xhtml files, the dates will be displayed at the index page.

### Display previews

The first `<p></p>` which is not `"date"` class will be previewed on the index page. The default preview length limit is 300 characters.

### Display tags

In your epub, you can specify the tags of an xhtml by placing a meta tag with `name="keywords"`, and then put the tags in `content` property and separate them by commas, e.g.
``` XHTML
<meta name="keywords" content="Scala, Java, BigData" />
```
If you choose to display tags, make sure to include the index.js file. Otherwise you don't need the js file.

### (Run from code) Use custom CSS and other configurations

There are more options if you call this tool in Python:

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
#     Your custom CSS (string) to use for generating index.html
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
