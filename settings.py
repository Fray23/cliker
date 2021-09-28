import os
import logging

logging.basicConfig(level=logging.DEBUG)

INSTAGRAM_LOGIN = os.getenv('INSTAGRAM_LOGIN')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

FULL_PROFILE = os.getenv('FULL_PROFILE')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
