import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_influencer_key_2024'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'Parth@18182'
    DB_NAME = os.environ.get('DB_NAME') or 'influencer_db'