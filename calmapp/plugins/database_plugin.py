from typing import TYPE_CHECKING

import mongoengine

from calmapp.plugins.plugin import Plugin

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class DatabasePlugin(Plugin):
    name = "database"

    def __init__(self, app: "App", config: "AppConfig"):
        super().__init__(app, config)

        conn_str = config.database.conn_str.get_secret_value()
        if conn_str:
            self._db = self._connect_db(conn_str, config.database.name,
                                        'main_database')

            self.logger.info(f"Discovered DATABASE_CONN_STR and connected successfully")
        # private_url = os.getenv('PRIVATE_MONGODB_URL')
        private_url = self.config.database.private_mongodb_url.get_secret_value()
        if private_url:
            self._private_db = self._connect_db(private_url,
                                                config.database.private_name,
                                                'private_database')
            self.logger.info(
                f"Discovered PRIVATE_MONGODB_URL and connected successfully")
        else:
            self._private_db = None

        # public_url = os.getenv('DATABASE_PUBLIC_MONGODB_URL')
        # public_url = os.getenv('PUBLIC_MONGODB_URL')
        public_url = config.database.public_mongodb_url.get_secret_value()
        if public_url:
            self._public_db = self._connect_db(public_url, config.database.public_name,
                                               'public_database')
            self.logger.info(
                f"Discovered PUBLIC_MONGODB_URL and connected successfully")
        else:
            self._public_db = None

    def _connect_db(self, conn_str, db_name, alias='default'):
        try:
            # Attempt to retrieve an existing connection by alias
            connection = mongoengine.get_connection(alias)
            if connection:
                # Validate if the current connection string matches the expected one
                if connection.host != conn_str:
                    self.logger.warning(
                        f"Warning: Connection string mismatch for alias {alias}")
                if connection.name != db_name:
                    self.logger.warning(
                        f"Warning: Database name mismatch for alias {alias}")
                return connection
        except mongoengine.connection.ConnectionFailure:
            # self.logger.error(f"Failed to retrieve connection by alias {alias}")
            self.logger.info("Existing connection not found, creating new connection")

        try:
            # Attempt to connect if no valid connection was retrieved

            return mongoengine.connect(
                db=db_name,
                host=conn_str,
                alias=alias
            )
        except mongoengine.connection.ConnectionFailure:
            self.logger.error(f"Failed to connect to database using alias {alias}")
            return None

    @property
    def db(self):
        return self._db or self._private_db or self._public_db
