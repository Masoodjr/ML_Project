import os
from dotenv import load_dotenv

load_dotenv()

class Credentials:
    email = os.getenv("email")
    password = os.getenv("password")

class Settings:
    MAX_PROFILES = 100000
    SCROLL_PAUSE = (0.5, 3.0)  # min and max pause time