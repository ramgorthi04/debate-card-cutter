## Simple Card Cutter
open-sourced. feel free to contribute if you want.
quick POC that we can cut cards with AI. 
this is an agent that takes an argument and autonomously researches and cuts evidence for it.
lots of errors, don't expect a great card cutter, but in a few years I'm sure the tech will be very capable.

## Set-up
**Python 3.10**
You need to create your own API keys and export on command line as 'perplexity_api_key' and 'openai_api_key'

Should cost about ~1-2 cents per card cut
```bash
python app.py
```

Hosts on port 5000 (http:// {your IP} :5000/)
Not hosted on any domain.

## Evidence Ethics Guarantees
- All outputted card-text is scraped via Python Beautiful Soup
- *Nothing* is added or deleted from what the HTTP request returns. This comes at the cost of significant design complexity and additional latency. 
- The citation is accurate to the best ability of the web scraping tool (which is pretty low).

> **Note:** There is no guarantee that highlighting preserves original author intent.

## Design
Takes as input an argument and the number of cards you want. 

## Links
Demo: https://www.youtube.com/watch?v=KWbeX9Txrrk&t=1s
Medium article: https://medium.com/@ramgorthi/cutting-debate-cards-with-ai-8484e966a1f8