from dotenv import load_dotenv
import os

load_dotenv()  # loads values from .env file

#protected config
SECRET_KEY = os.getenv("SECRET_KEY")

#general config
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30