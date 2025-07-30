import asyncio
import os
import logging

from src.web_scrapper import fetch_blog_content, parse_blog_content
from src.llm_agent import generate_podcast_script
from src.tts_converter import synthesize_conversation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def process_blog_to_podcast(blog_url: str, length_minutes: int = 5)-> None:
    """
    Processes a blog URL to generate a podcast script and convert it to audio.
    :param blog_url: URL of the blog to process.
    :param length_minutes: Length of the podcast in minutes.
    :return: None
    """
    logging.info(f"Starting processing for blog URL: {blog_url}")

    # Fetch blog content
    logging.info("Fetching blog content...")
    html_content = fetch_blog_content(blog_url)
    if not html_content:
        logging.error("Failed to fetch blog content.")
        return

    # Parse blog content
    logging.info("Parsing blog content...")
    blog_text = parse_blog_content(html_content)
    if not blog_text:
        logging.error("Failed to parse blog content.")
        return
    logging.info("Blog content successfully extracted, length: %d characters", len(blog_text))

    # Generate podcast script
    logging.info("Generating podcast script...")
    script = await generate_podcast_script(blog_text, length_minutes)
    if not script:
        logging.error("Failed to generate podcast script.")
        return
    logging.info(f"Podcast script successfully generated. Length: {len(script)} characters.")

    # Convert script to audio
    logging.info("Converting podcast script to audio...")
    audio_file_path = synthesize_conversation(script)
    if not audio_file_path:
        logging.error("Failed to convert podcast script to audio.")
        return
    logging.info(f"Podcast audio successfully created: {audio_file_path}")






def main():
    url = input("Enter the blog URL to process: ")
    asyncio.run(
        process_blog_to_podcast(
        blog_url = url
        )
    )


if __name__ == "__main__":
    main()
