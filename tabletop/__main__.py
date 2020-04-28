# This file is executed when running 'tabletop' as a module
import os
from dotenv import load_dotenv

load_dotenv('.env')
print(os.getenv('test'))
