#!/Users/ram/opt/anaconda3/bin/python

from openai import OpenAI
import openai
import os
import json
import re
# from docx import *
# from docx.shared import Pt
# from docx.enum.text import WD_UNDERLINE
# from docx.oxml.ns import qn
# from docx.oxml import OxmlElement
from scraper import *

def get_gpt_response(prompt, gpt_model="gpt-4", json_mode=False, response_format=""):
  """Encapsulates GPT prompting
  User provides prompt and gets only the text of GPT response

  Parameters
  ----------
  prompt : str
  gpt_model : str, optional (default is "gpt-4")
    Can also input "gpt-3.5-turbo"
  response_format : str, optional
    Input "json" for json format
  Returns
  -------
  str
    text response returned by chat completion agent
  None
    if no response received by GPT
  """

  client = OpenAI(
      api_key=os.environ.get("openai_api_key"),
  )
  if response_format == "json": 
    response = client.chat.completions.create(
    messages=[
      {
        "role": "user",
        "content": prompt,
      }
    ],
    response_format={ "type": "json_object" },
    model=gpt_model,
    )
  else:
    response = client.chat.completions.create(
    messages=[
      {
        "role": "user",
        "content": prompt,
      }
    ],
    model=gpt_model,
    )
  if response.choices:
    response_text = response.choices[0].message.content
    return response_text
  else:
    return None

def llm_get_text_to_underline(body_text, tag_line) -> list:
    """
    Given the following article text, returns a list of sentences/phrases to be underlined
    """
    sentence_endings = re.compile(r'[.!?]')
    # Find all matches of the sentence-ending punctuation
    sentences = sentence_endings.findall(body_text)
    
    # The number of sentences is the number of matches
    num_sentences = len(sentences)
    
    # Underline 50% of the sentences
    num_sentences_to_underline = int(num_sentences * 0.5)
    prompt = f"""Given the following article text, return a list of the sentences and phrases that best support this argument: {tag_line}. Aim to have {num_sentences_to_underline} sentences underlined.
    
    Return your response as a list in this form ["SENTENCE/PHRASE 1", "SENTENCE/PHRASE 2", "SENTENCE/PHRASE 3", ...]
    
    Article: {body_text}"""
    underlined_text_list = get_gpt_response(prompt, gpt_model="gpt-4-turbo", json_mode=True)
    
    # Try to load list into JSON and return
    try:
        underlined_text_list = json.loads(underlined_text_list)
    except json.decoder.JSONDecodeError as e:
        print(f"Error: {e}")
        print(underlined_text_list)
        return []
    
    return underlined_text_list

def llm_get_text_to_bold(underlined_text, num_words, tag_line) -> set:
    """
    Given underlined text, picks which words to bold. Returns a set of words that should be bolded.
    """
    # Bold 10% of the words
    num_words_to_bold = int(num_words*.1)
    prompt = f"""Given the following article text, return a list of the individual words that should be emphasized in speech to support this argument: {tag_line}. Aim to have at least {num_words_to_bold} words bolded.
    
    Return your response as a list in this form ["word 1", "word 2", "word 3", ...]
    Article text: {underlined_text}"""
    
    words_list = get_gpt_response(prompt, gpt_model="gpt-4-turbo")
    
    # Convert list to a set of words
    bolded_words = words_list.strip('[]').split(', ')
    word_set = set(bolded_words)
    return word_set


def llm_get_text_to_highlight(underlined_text, tag_line) -> list:
    """
    Given underlined text, picks which words to highlight. Returns a list of phrases/sentences that should be highlighted.
    """
    prompt = f"""Given the following article text, return a list of phrases/sentences that should be read out loud as evidence to support this argument {tag_line}. Only about 40-50 words should be highlighted.
    Return response as a list of this form ['PHRASE/SENTENCE 1', 'PHRASE/SENTENCE 2', 'PHRASE/SENTENCE 3', ...]
    Article text: {underlined_text}"""
    return get_gpt_response(prompt, gpt_model="gpt-4-turbo")

def llm_cut_article(title, author, date, body_text, tag_line) -> dict:
    """
    Given title, author, date, article text, and a tag line, returns a dictionary of sentences to be underlined, bolded, and highlighted based on the argument in the tag line.
    """
    # Get underlined sentences
    underlined_text_list = llm_get_text_to_underline(body_text, tag_line)
    # Flatten list into single string and count number of words underlined
    underlined_text = ""
    num_words = 0
    for text in underlined_text_list:
        num_words += len(text.split())
        # Add text to underlined_text
        underlined_text += " " + text + ""
    # Out of underlined sentences, pick words to bold
    bolded_text_set = llm_get_text_to_bold(underlined_text, num_words, tag_line)
    # Out of underlined sentences, pick phrases/sentences to read out-loud
    highlighted_text_list = llm_get_text_to_highlight(underlined_text, tag_line)
    
    card_formatting = {
        "underline": underlined_text_list,
        "bold": bolded_text_set,
        "highlight": highlighted_text_list
    }
    # Process the response
    return card_formatting

def format_card(card_formatting) -> None:
    pass 

url = 'https://www.democrats.senate.gov/newsroom/press-releases/majority-leader-schumer-floor-remarks-on-the-release-of-the-roadmap-for-ai-policy-by-the-senate-bipartisan-senate-ai-working-group'
article_info = scrape_article(url)

# Pass the extracted information to the call_openai_api function
title = article_info['title']
author = article_info['author']
date = article_info['date']
body_text = article_info['body']
tag_line = "There is a Senate AI bill on the floor now" 

print(json.dumps((llm_cut_article(title, author, date, body_text, tag_line)), indent=4))