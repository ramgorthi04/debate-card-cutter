## Simple Card Cutter
quick POC that we can cut cards with AI. 

goal is an agent that takes an argument and autonomously researches and cuts evidence for it. 

## Set-up
**Python 3.10**
Configure virtual environment (optional)

Perplexity research agent:
prototyped, but expensive and buggy (even more than the card cutter!).

Card-cutting agent:
```bash
pip install -r requirements.txt
python cutter.py "url" "tag-line"
```

## Evidence Ethics Guarantees
- All outputted card-text is scraped via Python Beautiful Soup
- *Nothing* is added or deleted from what the HTTP request returns. This comes at the cost of significant design complexity and additional latency. 
- The citation is accurate to the best ability of the web scraping tool (which is pretty low).

> **Note:** There is no guarantee that highlighting preserves original author intent.

## Design
Take as input URL and tag-line. Output word document with formatted and cited card.
Remainder of README is largely AI-generated based off my code.

### Scrape Website

1. **Index Card Text**
   - Formatting Table: `formatting_table[n][3]`

2. **Determine Relevant Sentences/Phrases for Argument**
   - Underline: `list[]`
   - Split into Words + Spaces/Symbols/Miscellaneous: `list[][]`

3. **Determine Words to Emphasize in Underlined Sentences**
   - Bold: `list[]`
   - Split into Words + Spaces/Symbols/Miscellaneous: `list[][]`

4. **Determine Words to Speak in Underlined Sentences**
   - Highlight: `list[]`
   - Split: `list[][]`

### Clean Lists in O(n)

- Ensure at least one of the words to the left or right of each word in underlined words matches either a left or right word in `all_words`. This check prevents the algorithm from underlining a non-existent sentence or phrase.

### Build Formatting Table in O(n)

- Use Index Pointers for Parallel List Traversal:
  - Check if the current word matches the current word in underline/bold/highlight list.
  - Always increment the `all_words` pointer.
  - Increment the underline/bold/highlight words pointer only on a match. This maintains the order of underlining/bolding/highlighting.

### Format Word Document in O(n)

- Build Card Citation with `article_info` from soup.
- Use Formatting Table to Build Maximal Runs of Continuous Formatting:
  - Create a new run if underlining/bolding/highlighting changes.
