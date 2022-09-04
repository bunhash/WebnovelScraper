README for making parsers

Parsers must implement the following:

* __init__(self, url)
* title(self) -> return title
* author(self) -> returns author
* cover(self) -> returns cover URL (in jpeg)
* chapters(self) -> returns list of chapter URLs
* parse_chapter(html): static -> returns parsed chapter HTML
