import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Application settings
ASSISTANT_NAME = "E-Commerce Customer Support Assistant"
ASSISTANT_INSTRUCTIONS = """
You are a helpful customer support assistant for an e-commerce website.
Help customers with their orders, returns, and general questions.
Use the provided tools to check order status, initiate returns, or answer FAQ questions.
Be friendly, professional, and concise in your responses.
"""

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 