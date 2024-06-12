## Set-up
**Python 3.10**
Configure virtual environment (optional)
```bash
pip install -r requirements.txt
python cutter.py
```

## Evidence Ethics Guarantees
- All outputted card-text was scraped via Python Beautiful Soup
- *Nothing* is added or deleted from what the HTTP request returns. This comes at the cost of significant design complexity and additional latency. 
- The citation is accurate to the best ability of the web scraping tool (which is pretty low).

> **Note:** There is no guarantee that highlighting preserves original author intent.

## Design
Take as input URL and tag-line. Output word document with formatted and cited card.

### Scrape website
Index card text -> formatting_table[n][3]
Determine sentences/phrases relevant to argument (underline) -> list[], split into words + spaces/symbols/miscellaneous -> list[][]
Determine words to emphasize (bold) in underlined sentences -> list[], split into words + spaces/symbols/miscellaneous -> list[][]
Determine words to speak (highlight) in underlined sentences -> list[], split -> list[][]

### Clean lists in O(n):
- Check that word(s) at lest one of the left and right of each word in underlined words matches either a left or right word in all_words. This check makes sure the algorithm won't trip by trying to underline a sentence or phrase that doesn't exist.

### Build formatting_table in O(n):
- Use index pointers for parallel list traversal
- Check if current word matches current word in underline/highlight/bold list. Always increment the all_words pointer, but only increment the underline/bold/highlight words pointer when we find a match. This maintains the order of the underlining/bolding/highlighting.

### Format word document in O(n):
- Build card citation with `article_info` from soup
- Use formatting table to build maximal runs of continuous formatting (if underlining/bolding/highlighting changes, we need to create a new run)