from enum import Enum
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    conn_str: Optional[SecretStr] = SecretStr("")
    name: str = "app_data"
    private_mongodb_url: Optional[SecretStr] = SecretStr("")
    private_name: str = "app_data"
    public_mongodb_url: Optional[SecretStr] = SecretStr("")
    public_name: str = "app_data"

    # todo: use enum?
    mode: str = "pymongo_single"

    model_config = {
        "env_prefix": "DATABASE_",
    }


class DatabaseMode(Enum):
    # just a single 'db' base with pymongo connection
    PYMONGO_SINGLE = "pymongo_single"

    # private and public databases with pymongo conneciton
    PYMONGO_PRIVATE_PUBLIC = "pymongo_private_public"

    # just a single 'db' base with mongoengine connection
    MONGOENGINE_SINGLE = "mongoengine_single"

    # private and public databases with mongoengine connection
    MONGOENGINE_PRIVATE_PUBLIC = "mongoengine_private_public"
