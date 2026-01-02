## differences

* no starting unordered lists w/`1\.`
* lists starting with indentation will get double-wrapped
  * i.e. `\n\t1. content` -> `<ol><ol><li>content</li></ol></ol>`
* the following elements will always be preceded by a newline, even at BOF:
    * `ul`
    * `ol`
    * `p`
