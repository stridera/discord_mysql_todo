import os
import dotenv
from dataclasses import dataclass

dotenv.load_dotenv()

@dataclass
class Config:
        host = os.getenv('MYSQL_HOST')
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        token = os.getenv('DISCORD_TOKEN')
        guild = int(os.getenv('GUILD_ID') or 0)

