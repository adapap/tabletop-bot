# Objects defined here will be importable using the namespace 'tabletop'
from dotenv import load_dotenv

from .client import Client

# Loads environments from .env file
load_dotenv('.env')

__author__ = 'adapap & ohm-nabar'
__version__ = '0.0.1'

print(f'Tabletop v{__version__} loaded.\n')
