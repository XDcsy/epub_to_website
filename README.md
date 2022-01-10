# epub_to_website
 
## Feature

It unpacks an epub book to a website-like sturcture with an auto-generated index page, which can then be directly opened (and hosted) as a website.

You may use it to host one epub book on the Internet. For example (my blog): https://xdcsy.github.io/

Or you may just open the index page locally, and use your browser as a primitive epub "reader".

## How to use
Get `epub_to_website.zip` at the release page, upzip it, and just drag and drop your epub file to `epub_to_website.exe` to run. (There are some customizable options. Please see below.)

An index page will be automatically generated. The title of the page will be the same as your epub title.

If you wish to host the epub as an website (e.g. on GitHub Pages), simply upload everything generated to your github.io repo.

## Options

You may tweak the following options in `run.properties` file.

Note: Some options are designed to display better index pages for notes and blogs, e.g. support for displaying dates and tags. In order to use them, the epub contents need to have some specific formats.

* `newFolder`:  
    Unpack the epub to the current directory or create a new folder. If enabled, the new folder will be named the title of the epub.

* `withTime`:  
    In your epub, if you have `<p class = "date"></p>` in the xhtml files, the dates will be displayed at the index page when enabled.

* `withPreview`:  
    When enabled, the first `<p></p>` which is not `"date"` class will be previewed on the index page.

* `previewMaxLen`:  
    Max number of characters displayed in each preview.

* `withTag`:  
    In your epub, you can specify the tags of an xhtml file by placing a meta tag with property `name="keywords"` and `content="keyword1,keyword2"`, separate them by commas. For example:  
    ``` XHTML
    <meta name="keywords" content="Scala, Java, BigData" />
    ```
    When enabled, the tags will appear on the top of the index page and be selective.

* `reversedOrder`:  
    When enabled, the articles will be displayed in reversed order on the index page.

* `epubEncoding` (default: `utf-8`):  
    Use this option to provide the encoding of the xhtml files in the original epub.

* `indexCSS` (default: `index.css`):  
    Path to CSS file for index page. There is one provided in the release.

* `pageCSS` (optional, default: `page.css`):   
    The CSS to inject into each xhtml page extracted from the epub. There is one provided in the release.  
    The purpuse of this CSS file is to make the xhtml pages more readable when rendered to web browsers. Comment it to disable.

### Run from code

``` Python3
from epub_to_website import epubToWebsite

epubToWebsite(inputFilePath = "path/to/epub/file",\
              indexCSS = "path/to/index.css",\
              pageCSS = "path/to/page.css",\
              newFolder = False,\
              withTime = False,\
              withPreview = False,\
              withTag = False,\
              reversedOrder = False,\
              previewMaxLen = 300)
```
