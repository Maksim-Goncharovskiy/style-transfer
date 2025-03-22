import dataclasses
import environs


@dataclasses.dataclass
class BotConfig:
    TOKEN: str
    ADMIN_IDS: list[int]
    DIR: str


@dataclasses.dataclass
class DatabaseConfig:
    HOST: str
    USER: str
    NAME: str
    PASSWORD: str


@dataclasses.dataclass
class Config:
    bot: BotConfig
    database: DatabaseConfig


def load_config() -> Config:
    env = environs.Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            TOKEN=env("BOT_TOKEN"),
            ADMIN_IDS=list(map(int, env.list("ADMIN_IDS"))),
            DIR=env("BOT_DIR")
        ),
        database=DatabaseConfig(
            HOST=env("HOST"),
            USER=env("USER"),
            NAME=env("NAME"),
            PASSWORD=env("PASSWORD")
        )
    )