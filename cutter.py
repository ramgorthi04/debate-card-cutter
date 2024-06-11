import json
import re
import logging
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_UNDERLINE
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from scraper import *
from tools import *

GPT_MODEL = "gpt-4o-2024-05-13"
# Configure logging
logging.basicConfig(filename='output.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def llm_get_text_to_underline(body_text: str, tag_line: str) -> list:
    """
    Given the following article text, returns a list of sentences/phrases to be underlined
    """
    logging.info('Calling llm_get_text_to_underline with body_text and tag_line.')
    
    sentence_endings = re.compile(r'[.!?]')
    # Find all matches of the sentence-ending punctuation
    sentences = sentence_endings.findall(body_text)
    
    # The number of sentences is the number of matches
    num_sentences = len(sentences)
    
    # Underline 50% of the sentences
    num_sentences_to_underline = int(num_sentences * 0.5)
    prompt = f"""Given the following article text, return a list of the sentences and phrases that best support this argument: {tag_line}. Aim to have {num_sentences_to_underline} sentences underlined.
    
    Return your response as a JSON in this form ["SENTENCE/PHRASE 1", "SENTENCE/PHRASE 2", "SENTENCE/PHRASE 3", ...]
    
    Article: {body_text}"""
    underlined_text_list = get_gpt_response(prompt, gpt_model=GPT_MODEL, json_mode=True)
    underlined_text_list = underlined_text_list[7:]
    underlined_text_list = underlined_text_list[:-3]

    # Try to load list into JSON and return
    try:
        underlined_text_list = json.loads(underlined_text_list)
        logging.info('Underlined text list successfully parsed.')
    except json.decoder.JSONDecodeError as e:
        logging.error(f"Error parsing underlined text list: {e}")
        logging.error(underlined_text_list)
        return []
    
    logging.info(f"Underlined text list: {underlined_text_list}")
    return underlined_text_list

def llm_get_text_to_bold(underlined_text: str, num_words: int, tag_line: str) -> list:
    """
    Given underlined text, picks which words to bold. Returns a list of words that should be bolded.
    """
    logging.info('Calling llm_get_text_to_bold with underlined_text and tag_line.')

    # Bold ~10% of the words
    num_words_to_bold = int(num_words * 0.1)
    prompt = f"""Given the following article text, return a list of the individual words that should be emphasized in speech to support this argument: {tag_line}. Aim to have at least {num_words_to_bold} words bolded.
    
    Return your response as a JSON in this form ["word 1", "word 2", "word 3", ...]
    Article text: {underlined_text}"""
    
    words_list = get_gpt_response(prompt, gpt_model=GPT_MODEL, json_mode=True)
    words_list = words_list[7:]
    words_list = words_list[:-3]

    # Convert list to a set of words
    bolded_words = words_list.strip('[]').split(', ')
    bolded_list = json.loads(bolded_words)
    
    logging.info(f"Bolded words list: {bolded_list}")
    return bolded_list

def llm_get_text_to_highlight(underlined_text: str, tag_line: str) -> list:
    """
    Given underlined text, picks which words to highlight. Returns a list of phrases/sentences that should be highlighted.
    """
    logging.info('Calling llm_get_text_to_highlight with underlined_text and tag_line.')

    prompt = f"""Given the following article text, return a list of phrases/sentences that should be read out loud as evidence to support this argument {tag_line}. Only about 40-50 words should be highlighted.
    Return response as a JSON of this form ['PHRASE/SENTENCE 1', 'PHRASE/SENTENCE 2', 'PHRASE/SENTENCE 3', ...]
    Article text: {underlined_text}"""
    
    highlighted_text = get_gpt_response(prompt, gpt_model=GPT_MODEL, json_mode=True)
    highlighted_text = highlighted_text[7:]
    highlighted_text = highlighted_text[:-3]

    logging.info(f"Highlighted text list: {highlighted_text}")
    return highlighted_text

def llm_cut_article(title: str, author: str, date: str, body_text: str, tag_line: str) -> dict:
    """
    Given title, author, date, article text, and a tag line, returns a dictionary of sentences to be underlined, bolded, and highlighted based on the argument in the tag line.
    """
    logging.info(f'Calling llm_cut_article with title: {title}, author: {author}, date: {date}, tag_line: {tag_line}.')

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
    bolded_text_list = llm_get_text_to_bold(underlined_text, num_words, tag_line)
    # Out of underlined sentences, pick phrases/sentences to read out-loud
    highlighted_text_list = llm_get_text_to_highlight(underlined_text, tag_line)
    
    logging.info(f'Underlined text list: {underlined_text_list}')
    logging.info(f'Bolded text list: {bolded_text_list}')
    logging.info(f'Highlighted text list: {highlighted_text_list}')

    return underlined_text_list, bolded_text_list, highlighted_text_list

def split_string(text: str) -> list:
    """
    Returns list of words, spaces, punctuation, numbers, and paragraph breaks in string
    """
    pattern = r'\w+|[^\w\s]|\s+|\n\n+'
    
    # Split the text according to the pattern
    elements = re.findall(pattern, text)
    
    return elements

def add_run_to_paragraph(p, run, underline, bold, highlight):
    run = p.add_run(run)
    run.underline = underline
    run.bold = bold
    font = run.font
    font.name = 'Calibri'
    if underline:
        font.size = Pt(11)
    else:
        font.size = Pt(8)
        r = run._element
        r.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
        r.rPr.rFonts.set(qn('w:ascii'), 'Calibri')
        r.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
        r.rPr.rFonts.set(qn('w:cs'), 'Calibri')
            
    if highlight:
        run.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN

def format_card(tag: str, all_text: str, underlined_text_list: list, bolded_text_list: set, highlighted_text_list: list) -> None:
    """Produces word document. Underlines, bolds, and highlights words in the word document."""
    
    # Create card header with tag, author, date, citation
    # TODO: Implement

    # Build a formatting table: list of triples [word/space/punctuation: str, underline: bool, bold: bool, highlight: bool]
    formatting_table = []
    
    # Split all_text according to split_string
    text_elements = split_string(all_text)
    
    # Break underlined_text_list and highlighted_text_list according to split_string 
    underlined_elements = []
    for list in underlined_text_list:
        underlined_elements.extend(split_string(list))    
    bolded_elements = bolded_text_list
    highlighted_elements = []
    for list in highlighted_text_list:
        highlighted_elements.extend(split_string(list))
        
    # Now, we determine which elements in text_elements should be underlined, bolded, and highlighted
    text_pointer = 0
    underlined_pointer = 0
    bolded_pointer = 0
    highlighted_pointer = 0
    
    # Iterate through text_elements, determine if each element should be underlined, bolded, and/or highlighted
    while text_pointer <= (len(text_elements)-1):
        underlined = False
        bolded = False
        highlighted = False
        
        if (underlined_pointer <= (len(underlined_elements)-1)) and (text_elements[text_pointer] == underlined_elements[underlined_pointer]):
            underlined_pointer += 1
            underlined = True
            if (bolded_pointer <= (len(bolded_elements)-1)) and (text_elements[text_pointer] == bolded_elements[bolded_pointer]):
                bolded_pointer += 1
                bolded = True
            if (highlighted_pointer <= (len(highlighted_elements)-1)) and (text_elements[text_pointer] == highlighted_elements[highlighted_pointer]):
                highlighted_pointer += 1
                highlighted = True
            
        formatting_table.append([text_elements[text_pointer], underlined, bolded, highlighted])
        text_pointer += 1

    
    # Now we have the formatting table, we can create the word document
    doc = Document()
    runs = []
    run_index = 0
    
    p = doc.add_paragraph()
    
    element_pointer = 0
    element = formatting_table[element_pointer]

    curr_run_underline = element[1]
    curr_run_bold = element[2]
    curr_run_highlight = element[3]
    
    # Create the run as we go. Stop the run when formatting changes
    runs.append(element[0])
    element_pointer += 1
    
    while element_pointer <= (len(formatting_table)-2):
        element_pointer += 1
        element = formatting_table[element_pointer]
        # if '\n' in element[0]:
        #     p = doc.add_paragraph()
        # Continue the run until a formatting change
        if (element[1] == curr_run_underline) and (element[2] == curr_run_bold) and (element[3] == curr_run_highlight):
            runs[run_index] += element[0]
        else:
            # Formatting has changed. Add the run and re-set formatting to new values.
            add_run_to_paragraph(p, runs[run_index], curr_run_underline, curr_run_bold, curr_run_highlight)
            # runs[run_index] = p.add_run(runs[run_index])
            # runs[run_index].underline = curr_run_underline
            # runs[run_index].bold = curr_run_bold
            # font = runs[run_index].font
            # font.name = 'Calibri'
            # if curr_run_underline:
            #     font.size = Pt(11)
            # else:
            #     font.size = Pt(8)
            # r = runs[run_index]._element
            # r.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
            # r.rPr.rFonts.set(qn('w:ascii'), 'Calibri')
            # r.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
            # r.rPr.rFonts.set(qn('w:cs'), 'Calibri')
            
            # if curr_run_highlight:
            #     runs[run_index].font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
            
            # Start a new run with new formatting
            curr_run_underline = element[1]
            curr_run_bold = element[2]
            curr_run_highlight = element[3]
            run_index += 1
            runs.append(element[0])    
    add_run_to_paragraph(p, runs[run_index], curr_run_underline, curr_run_bold, curr_run_highlight)
    
    doc.save(f'{tag}.docx')
    print(f"Document {tag}.docx created successfully")
                

def cut_card(tag: str, url: str) -> None:
    # Scrape article info (author, date, title, body)
    article_info = scrape_article(url)
    
    # Pass the extracted information to the card cutting function
    title = article_info['title']
    author = article_info['author']
    date = article_info['date']
    body_text = article_info['body']
    tag_line = tag

    underlined_text_list, bolded_text_list, highlighted_text_list = llm_cut_article(title, author, date, body_text, tag_line)
    
    # Prepare a dictionary for JSON serialization (excluding the set)
    card_formatting = {
        "underline": underlined_text_list,
        "bold": bolded_text_list,
        "highlight": highlighted_text_list
    }
    
    print(json.dumps(card_formatting, indent=4))
    # Log the output
    logging.info(f'Final card formatting: {json.dumps(card_formatting, indent=4)}')
    
    format_card(tag, body_text, underlined_text_list, bolded_text_list, highlighted_text_list)

    
if __name__ == '__main__':
    url = 'https://www.democrats.senate.gov/newsroom/press-releases/majority-leader-schumer-floor-remarks-on-the-release-of-the-roadmap-for-ai-policy-by-the-senate-bipartisan-senate-ai-working-group'
    tag = "The Senate AI bill passes now."
    cut_card(tag, url)
    
