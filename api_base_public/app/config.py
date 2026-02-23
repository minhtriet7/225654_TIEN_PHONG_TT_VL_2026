# File cấu hình chung cho ứng dụng

import os
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()


class Settings:
    # SETTING
    DIR_ROOT = os.path.dirname(os.path.abspath(".env"))
    
    # API KEY
    API_KEY = os.environ["API_KEY"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    
    # SECURITY
    ALLOW_ORIGINS = os.environ["ALLOW_ORIGINS"]

    # TITLE
    TITLE_APP = os.environ["TITLE_APP"]
    VERSION_APP = os.environ["VERSION_APP"]
    

    # DB
    HOST = os.environ["HOST"]
    USER = os.environ["USER"]
    PASSWORD = os.environ["PASSWORD"]
    DATABASE = os.environ["DATABASE"]


settings = Settings()
