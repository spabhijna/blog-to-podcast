Blog-to-Podcast

A Python project that transforms blog articles into podcasts. It scrapes blog content, summarizes it with an LLM, and converts it into audio using a text-to-speech engine.

Features

- Web scraping: Extracts text content from blog URLs.

- LLM agent: Summarizes or reformats content for natural narration.

- Text-to-Speech: Converts text into high-quality audio.

- Podcast-ready output: Exports .mp3 files in the output/ folder.

- Command-line interface: Run the pipeline end-to-end with a single command.

📂 Project Structure
```plaintext
blog-to-podcast/
│── src/
│   ├── main.py         # Entry point
│   ├── parser.py       # Blog/text extractor
│   ├── tts_engine.py   # Text-to-speech logic
│   ├── utils.py        # Helpers
│── pyproject.toml      # Project + dependency manager (uv)
│── README.md
```
⚡ Installation

Clone the repository:

```bash
git clone git@github.com:spabhijna/blog-to-podcast.git
cd blog-to-podcast
```

Install dependencies using uv:
```bash
uv sync
```

🛠️ Usage

Convert a blog post from a URL:

```bash
uv run src/main.py 
```

The generated audio will be saved in the output/ folder.

Roadmap

- Web UI version.

- Publish directly to Spotify/Apple Podcasts.

- RSS feed auto-generation.

- Multi-language TTS support.

Contributing

PRs and issues are welcome!

License

MIT License.