import json
import requests
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    """
    AWS Lambda handler for scraping homepage text.
    Expects an event with the following JSON structure:
    {
        "url": "https://example.com"
    }

    Returns:
    - JSON with the scraped text or an error message.
    """
    try:
        # Extract URL from the event
        body = json.loads(event['body'])
        url = body.get("url")
        if not url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'url' in request body"})
            }

        # Scrape the homepage text
        result = scrape_homepage_text(url)
        return {
            "statusCode": 200,
            "body": json.dumps({"text": result})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def scrape_homepage_text(url, timeout=10):
    """
    Scrapes the text content from the homepage of a given URL.
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/"
        }

        session = requests.Session()
        session.headers.update(headers)

        response = session.get(url, timeout=timeout)
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'noscript']):
            script_or_style.decompose()

        # Get text and clean it
        text = soup.get_text(separator=' ', strip=True)
        return text

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
