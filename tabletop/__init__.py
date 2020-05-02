# Objects defined here will be importable using the namespace 'tabletop'
from dotenv import load_dotenv
# Loads environments from .env file
load_dotenv('.env')

from .client import Client
