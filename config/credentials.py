import os
from dotenv import load_dotenv

load_dotenv()

class Credentials:
    email = os.getenv("email")
    password = os.getenv("password")
