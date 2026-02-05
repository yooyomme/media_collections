from pydantic_settings import BaseSettings
import os


def get_database_url() -> str:
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')
    name = os.environ.get('DB_NAME')
    database_url = f'mysql+aiomysql://{user}:{password}@database:{port}/{name}'
    return database_url

def get_project_name() -> str:
    project_name = os.environ.get('PROJECT_NAME')
    return project_name


class Settings(BaseSettings):
    PROJECT_NAME: str = get_project_name()
    DATABASE_URL: str = get_database_url()

    class Config:
        env_file = '../.env'
        extra = 'ignore'


settings = Settings()