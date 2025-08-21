import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_blog_content(url: str) -> str | None:
    """
    Fetches HTML content from a given URL.
    :param url: URL of the blog to scrape.
    :return: str|None: HTML content of the blog or None if an error occurs.
    """

    try:
        logging.info(f"Fetching content from {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url=url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        logging.info(f"Successfully fetched content from {url}")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching content from {url}: {e}")
        return None


def parse_blog_content(html_content: str) -> str | None:
    """
        Parses the HTML content to extract the main text of the blog post.

    :param html_content: HTML content of the blog post.
    :return: Extracted Plain text or None if parsing fails.
    """

    soup = BeautifulSoup(html_content, "html.parser")

    selectors = [
        "article.content",
        "article.post-content",
        "div.entry-content",
        "div.post-content",
        "div.blog-content",
        "div.main-content",
        "main#content",
    ]

    content_elements = []
    for selector in selectors:
        content_elements.extend(soup.select(selector))

    text_parts = []
    seen_texts = set()

    if content_elements:
        for element in content_elements:
            for s in element(["script", "style"]):
                s.extract()
            text = element.get_text(separator="\n", strip=True)
            if text not in seen_texts:
                text_parts.append(text)
                seen_texts.add(text)
    elif soup.body:
        logging.warning(
            "No specific content elements found. Extracting text from body."
        )
        text_parts.append(soup.body.get_text(separator="\n", strip=True))
    else:
        logging.warning("No <body> tag found. Returning empty string.")
        return ""

    return "\n\n".join(text_parts).strip()


if __name__ == "__main__":
    # Example usage:
    test_url = "https://blog.google/products/shopping/back-to-school-ai-updates-try-on-price-alerts/"
    html = fetch_blog_content(test_url)
    if html:
        extracted_text = parse_blog_content(html)
        print("--- Extracted Blog Text ---")
        print(extracted_text[:1000])  # Print first 1000 characters for brevity
        print("...")
    else:
        print("Failed to retrieve blog content.")
