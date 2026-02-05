import requests
from bs4 import BeautifulSoup
from typing import Tuple, List
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from settings import MODEL_NAME, WEB_CONTENT_WORD_LIMIT


class ParsingError(Exception):
    pass


class WebLinkAnalyzer:
    """Agent for analyzing web links and generating tags"""

    def __init__(self, model_name: str = MODEL_NAME):
        self.llm = OllamaLLM(model=model_name)
        self.word_limit = WEB_CONTENT_WORD_LIMIT
        self.prompt_template = PromptTemplate(
            input_variables=["content"],
            template="""Analyze the following web page content and provide:
1. Up to 5 relevant tags (keywords) that describe the content
2. A brief description in maximum 3 sentences

Content:
{content}

Provide your response in this exact format:
TAGS: tag1, tag2, tag3, tag4, tag5
DESCRIPTION: Your description here.""",
        )

    def fetch_content(self, url: str) -> str:
        """Fetch and extract first 200 words from web page"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = " ".join(chunk for chunk in chunks if chunk)

            # Get first N words based on configuration
            words = text.split()[:self.word_limit]
            return " ".join(words)

        except Exception as e:
            raise Exception(f"Failed to fetch content from {url}: {str(e)}")

    def analyze(self, url: str) -> Tuple[List[str], str]:
        """Analyze web link and return tags and description"""
        content = self.fetch_content(url)

        prompt = self.prompt_template.format(content=content)
        response = self.llm.invoke(prompt)

        # Parse response
        tags = []
        description = ""

        lines = response.strip().split("\n")
        for line in lines:
            if line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                tags = tags[:5]  # Maximum 5 tags
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()

        # Fallback if parsing failed
        if not tags or not description:
            raise ParsingError("Unable to parse provided content.")

        return tags, description
