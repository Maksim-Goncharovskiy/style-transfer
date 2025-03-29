import dataclasses
import environs


@dataclasses.dataclass
class BotConfig:
    TOKEN: str
    ADMIN_IDS: list[int]
    DIR: str


@dataclasses.dataclass
class RedisConfig:
    HOST: str
    PORT: int


@dataclasses.dataclass
class Config:
    bot: BotConfig
    redis: RedisConfig


def load_config() -> Config:
    env = environs.Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            TOKEN=env("BOT_TOKEN"),
            ADMIN_IDS=list(map(int, env.list("ADMIN_IDS"))),
            DIR=env("BOT_DIR")
        ),
        redis=RedisConfig(
            HOST=env("REDIS_HOST"),
            PORT=env("REDIS_PORT")
        )
    )
