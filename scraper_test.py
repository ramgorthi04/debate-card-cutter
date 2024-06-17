import requests
import fitz  # PyMuPDF
from io import BytesIO
from bs4 import BeautifulSoup

def extract_text_from_pdf_content(pdf_content):
    try:
        document = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF content: {e}")
        return ""

def extract_metadata_from_text(text):
    lines = text.split('\n')
    author = None
    date_published = None
    publisher = None
    title = None
    author_qualifications = None
    body_start_index = 0

    for i, line in enumerate(lines):
        if 'author' in line.lower():
            author = line.split(':', 1)[-1].strip()
        elif 'published' in line.lower() or 'date' in line.lower():
            date_published = line.split(':', 1)[-1].strip()
        elif 'publisher' in line.lower():
            publisher = line.split(':', 1)[-1].strip()
        elif 'qualification' in line.lower() or 'degree' in line.lower():
            author_qualifications = line.split(':', 1)[-1].strip()
        elif title is None and len(line.strip()) > 0:
            title = line.strip()
            body_start_index = i + 1

    body_text = '\n'.join(lines[body_start_index:])

    return {
        "title": title,
        "author": author,
        "author_qualifications": author_qualifications,
        "date_published": date_published,
        "publisher": publisher,
        "body_text": body_text
    }

def extract_metadata_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('title').text if soup.find('title') else None
    author = None
    date_published = None
    publisher = None
    author_qualifications = None

    # Add more sophisticated parsing if the website has specific metadata tags
    # This example assumes meta tags and certain classes/ids contain the information
    if soup.find('meta', {'name': 'author'}):
        author = soup.find('meta', {'name': 'author'})['content']
    if soup.find('meta', {'name': 'date'}):
        date_published = soup.find('meta', {'name': 'date'})['content']
    if soup.find('meta', {'name': 'publisher'}):
        publisher = soup.find('meta', {'name': 'publisher'})['content']
    if soup.find('meta', {'name': 'qualification'}):
        author_qualifications = soup.find('meta', {'name': 'qualification'})['content']

    body_text = ''
    if soup.find('body'):
        body_text = ' '.join([p.text for p in soup.find_all('p')])
    # Replace ever double quote with a single quote in body_text
    body_text = body_text.replace('"', "'")
    return {
        "title": title,
        "author": author,
        "qualifications": author_qualifications,
        "date": date_published,
        "publication": publisher,
        "body": body_text
    }

def scrape_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type:
            pdf_content = BytesIO(response.content)
            print("PDF content fetched successfully!")
            pdf_text = extract_text_from_pdf_content(pdf_content)
            metadata = extract_metadata_from_text(pdf_text)
        elif 'text/html' in content_type:
            print("HTML content fetched successfully!")
            html_content = response.content
            metadata = extract_metadata_from_html(html_content)
        else:
            raise Exception(f"Unsupported content type: {content_type}")
    else:
        raise Exception(f"Failed to fetch content. Status code: {response.status_code}")

    metadata['url'] = url

    return metadata

# Example usage:
if __name__ == "__main__":
    url = "https://chicagounbound.uchicago.edu/cgi/viewcontent.cgi?article=2696&context=law_and_economics"
    article_info = scrape_article(url)
    print(article_info)
