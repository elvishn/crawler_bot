from dataclasses import dataclass
from environs import Env
from typing import Optional
import os


@dataclass
class TgBot:
    token: str

@dataclass
class DatabaseConfig:
    path: str  # Путь к SQLite файлу

@dataclass
class PathsConfig:
    uploads_dir: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    paths: PathsConfig


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, "data", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN')
        ),
        db=DatabaseConfig(
            path=os.path.join(base_dir, "data", "sites.db")
        ),
        paths=PathsConfig(
            uploads_dir=uploads_dir
        )

    )
