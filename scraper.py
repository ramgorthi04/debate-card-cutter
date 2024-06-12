import requests
from bs4 import BeautifulSoup
from http.client import RemoteDisconnected
from requests.exceptions import Timeout

def scrape_article(url) -> dict:
    """
    Returns title, body, author, date, qualifications, publication, url"""
    try:
        page = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
    except requests.exceptions.ConnectionError as e:
        if isinstance(e.args[0], RemoteDisconnected):
            print("Failed to scrape article")
            print("RemoteDisconnected: The remote end closed connection without response")
        else:
            print("Failed to scrape article")
            print("Other ConnectionError occurred")
        return None
    except Timeout:
        print("Failed to scrape article")
        print("The request timed out after 10 seconds.")
        return None
    except Exception as e:
        print("Failed to scrape article")
        print(f"An unexpected error occurred: {e}")
        return None

    if page.status_code != 200:
        print(f"Failed to retrieve the webpage, status code: {page.status_code}")
        return None

    soup = BeautifulSoup(page.content, "html.parser")

    # Extract title
    title_tag = soup.find('h1')
    title = title_tag.get_text() if title_tag else 'No title found'

    # Extract body with preserved paragraph breaks
    paragraphs = soup.find_all("p")
    body = "\n\n".join([p.get_text() for p in paragraphs]) if paragraphs else 'No body found'

    # Extract author
    author_tag = soup.find('span', class_='story-meta__author')
    author = author_tag.get_text().strip() if author_tag else 'No author'

    # Extract date
    date_tag = soup.find('time', class_='timestamp')
    date = date_tag.get_text().strip() if date_tag else 'No date'

    # Extract author qualifications
    qualifications_tag = soup.find('span', class_='author-qualifications')
    qualifications = qualifications_tag.get_text().strip() if qualifications_tag else 'No qualifications found'

    # Extract publication/journal name
    publication_tag = soup.find('span', class_='publication-name')
    publication = publication_tag.get_text().strip() if publication_tag else 'No publication found'

    # # Print the results
    # print(f'Title: {title}')
    # print(f'Author: {author}')
    # print(f'Date: {date}')
    # print('-' * 80)
    # print(f'Body: {body}') 
    if __debug__:
        print(body)
    return {
        'title': title,
        'body': body,
        'author': author,
        'date': date,
        'qualifications': qualifications,
        'publication': publication,
        'url': url
    }

    
if __name__ == '__main__':
    # URL of the article to scrape
    url = 'https://www.federalreserve.gov/econres/feds/redistribution-and-the-monetary-fiscal-policy-mix.htm'
    scrape_article(url)
