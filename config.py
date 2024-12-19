import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard_to_guess_secret_key'
    DB_PATH = 'fastfood.db'
