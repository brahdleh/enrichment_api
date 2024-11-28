import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import openai

# Configure OpenAI library to use Azure
openai.api_type = "azure"
openai.api_base = "https://preprod-obai.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "5c450e93bf58454b8a177835e14596d9"


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

    # Extract URL from the event
    try:
        body = json.loads(event['body'])
        url = body.get("url")
        if not url:
            return {
                "statusCode": 1,
                "body": json.dumps({"error": "Missing 'url' in request body"})
            }

    except Exception as e:
        return {
            "statusCode": 2,
            "body": json.dumps({"JSON error": str(e)})
        }
    
    # Validate the URL
    is_valid, error_message = validate_url(url)
    if not is_valid:
        return {
            "statusCode": 2,
            "body": json.dumps({"error": "Invalid URL"})
        }

    # Scrape the homepage text
    result = scrape_homepage_text(url)

    # Summarize the homepage text
    result = summarize_content
        


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

        try:
            response.raise_for_status()  # Raises HTTPError for bad responses
        except requests.exceptions.HTTPError as e:
            return {
                "statusCode": 3,
                "body": json.dumps({"error": str(e)})
            }

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'noscript']):
            script_or_style.decompose()

        # Get text and clean it
        text = soup.get_text(separator=' ', strip=True)
        return text

    except requests.exceptions.RequestException as e:
        return {
            "statusCode": 4,
            "body": json.dumps({"Request error": str(e)})
        }



def validate_url(url: str):
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True, None
        else:
            return False, "Invalid URL format"
    except Exception as e:
        return False, str(e)



def summarize_content(text: str, max_tokens=200):
    """
    Summarizes the given text using Azure OpenAI.

    Parameters:
    - text (str): The text to summarize.
    - max_tokens (int): The maximum number of tokens for the summary.

    Returns:
    - str: The summarized text, or an error message.
    """
    try:
        if text.startswith("error:") or text=="":
            return text  # Skip summarization for error messages

        messages = [
            {"role": "system", "content": "You are a helpful assistant that concisely summarises company information."},
            {"role": "user", "content": f"Please provide a concise paragraph fewer than 50 words summarising this company's products and services and target audience. Be objective and clear about what the company actually creates and provides, ignoring marketing.:\n\n{text}"}  
        ]

        response = openai.ChatCompletion.create(
            engine="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        summary = response['choices'][0]['message']['content'].strip()
        return summary

    except Exception as e:
        return f"Summary Error: {e}"