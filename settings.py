"""
Application settings and configuration
"""

# AI Model Configuration
# The model to use for text and web link analysis
# Must have Ollama installed and the model pulled locally
MODEL_NAME = "llama3.2:3b"

# Alternative model options by RAM requirements:

# For 8GB RAM (use smaller, faster models):
# MODEL_NAME = "llama3.2:1b"             # Very fast, decent quality
# MODEL_NAME = "qwen2.5:3b"              # Fast and efficient, good balance
# MODEL_NAME = "gemma2:2b"               # Google's lightweight model

# For 16GB RAM (recommended - balanced performance):
# MODEL_NAME = "llama3.2:3b"             # Default - best balance (recommended)
# MODEL_NAME = "mistral:latest"          # Good alternative, fast performance
# MODEL_NAME = "phi3:latest"             # Microsoft's efficient model
# MODEL_NAME = "qwen2.5:7b"              # Higher quality than 3b version

# For 32GB RAM (use larger, higher quality models):
# MODEL_NAME = "llama3.1:8b"             # High quality, OpenAI-level performance
# MODEL_NAME = "llama3.3:70b"            # Excellent quality, slower processing

# To use a different model:
# 1. Pull it with Ollama: ollama pull <model-name>
# 2. Update MODEL_NAME above
# 3. Restart the application

# Web Content Configuration
WEB_CONTENT_WORD_LIMIT = 200  # Number of words to extract from web pages
