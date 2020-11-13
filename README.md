# epub_to_website
 
## What is this
It's a simple script that unpacks an epub ebook to a website-like sturcture, which can then be directly uploaded and hosted at places like GitHub pages.

Example: https://xdcsy.github.io/

## How to use
Get `epub_to_website.exe` at the release page, and just drag and drop your epub file to the exe.

If you are using GitHub pages, simply upload everything unpacked to your github.io repo, and it should work.

Or if you prefer to call it in Python:

``` Python3
from epub_to_website import epubToWebsite
epubToWebsite("path/to/epub/file", CSS = "body {width: 1200px}", newFolder = True)

# CSS:
#     your custom CSS to use for generating index.html
# newFolder (default: False):
#     unpack to the current directory or create a new folder.
#     If True, folder name will be the title of the ebook.
```
