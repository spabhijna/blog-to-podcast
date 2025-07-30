import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import asyncio

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Google Generative AI API
try:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    logging.info("Google Generative AI API configured successfully.")
except Exception as e:
    logging.error(f"Failed to configure Google Generative AI API: {e}")

async def generate_podcast_script(blog_text:str, length_minutes:int=5)->str|None:
    """
    Generates a podcast script based on the provided blog text and desired length in minutes.
    :param blog_text: The full text content of the blog post.
    :param length_minutes: Desired length of the podcast script in minutes.
    :return: str|None: Generated podcast script or None if an error occurs.
    """

    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = (
        f"You are an expert podcast scriptwriter and content creator. Your goal is to transform "
        f"the following detailed blog post into a dynamic and engaging podcast script. "
        f"The script should contain host and guest interactions."
        f"The Sccript should not have any sound effects or music, just the script for the podcast. "
        f"""Example format of the script:
            [HOST] Welcome to the podcast! Today, we have a very special guest with us. How are you doing today?
            [GUEST] I'm doing great, thank you for having me! It's wonderful to be here.
            [HOST] It's our pleasure. We're going to talk about some exciting new developments in AI.
            [GUEST] Yes, I'm really looking forward to diving into that.
            [HOST] Fantastic. Let's start with your latest research."""
        f"The podcast should be approximately {length_minutes} minutes long, so condense the information "
        f"effectively while retaining all crucial insights and key takeaways. "
        f"Structure the script with a clear introduction, 3-4 distinct main segments (each focusing on a core idea from the blog), "
        f"and a compelling conclusion. "
        f"Adopt a conversational, informative, and slightly enthusiastic tone. "
        f"Consider using speaker labels (e.g., 'HOST:', 'NARRATOR:') to make the script easy to follow for audio production. "
        f"Ensure smooth transitions between segments. Avoid jargon where possible, or explain it simply. "
        f"Make it sound natural for spoken word, not just read text.\n\n"
        f"--- Blog Post Content ---\n{blog_text}\n\n"
        f"--- Podcast Script ---\n"
    )

    try:
        logging.info("Sending request to Google Generative AI for podcast script generation...")

        response = await model.generate_content_async(prompt)

        # Check for valid response structure
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            script = response.candidates[0].content.parts[0].text
            logging.info("Podcast script generated successfully.")
            return script
        else:
            logging.error("Error generating podcast script")
            return None
    except Exception as e:
        logging.error(f"Error generating podcast script with Gemini: {e}")
        return None

if __name__ == "__main__":
    # This is a placeholder for testing. In a real scenario, you'd get
    # blog_text from the web_scraper.py module.
    sample_blog_content = """
    Artificial intelligence (AI) is rapidly transforming various industries, from healthcare to finance,
    and is poised to reshape many aspects of daily life. One of the most exciting advancements is in
    natural language processing (NLP), which allows machines to understand, interpret, and generate
    human language with remarkable fluency. This capability has led to significant breakthroughs in
    applications such as intelligent chatbots that can hold surprisingly human-like conversations,
    highly accurate real-time translation services that break down language barriers, and automated
    content creation tools that can draft articles, summaries, and even creative writing.
    The future of AI promises even more profound integration into daily life, with implications for
    personal assistants, autonomous vehicles, and personalized education. However, this rapid progress
    also raises important questions about ethics, privacy, job displacement, and the broader societal
    impact of increasingly intelligent machines. Addressing these challenges responsibly will be critical
    as AI continues to evolve.
    """
    print("Attempting to generate a 2-minute script from sample content...")
    # Use asyncio.run to execute the async function
    generated_script = asyncio.run(generate_podcast_script(sample_blog_content, length_minutes=2))
    if generated_script:
        print("\n--- Generated Podcast Script ---")
        print(generated_script)
    else:
        print("Failed to generate script for sample content.")
