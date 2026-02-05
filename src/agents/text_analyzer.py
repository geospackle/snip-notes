from typing import Tuple, List
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from settings import MODEL_NAME


class TextAnalyzer:
    """Agent for analyzing text and generating tags"""

    def __init__(self, model_name: str = MODEL_NAME):
        self.llm = OllamaLLM(model=model_name)
        self.prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""Analyze the following text and provide:
1. Up to 5 relevant tags (keywords) that describe what the text is about
2. A brief description in maximum 3 sentences

Text:
{text}

Provide your response in this exact format:
TAGS: tag1, tag2, tag3, tag4, tag5
DESCRIPTION: Your description here.""",
        )

    def analyze(self, text: str) -> Tuple[List[str], str]:
        """Analyze text and return tags and description"""
        prompt = self.prompt_template.format(text=text)
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
        if not tags:
            tags = ["text", "note"]
        if not description:
            description = text[:200] + "..." if len(text) > 200 else text

        return tags, description
