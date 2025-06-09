import yaml
import os
import sqlalchemy
from sqlalchemy import text
class DatabaseConnector:
    def __init__(self, config_path='configs/database.yaml'):
        self.config_path = config_path
        self.config = self._load_config()
        self.engine = self._create_engine()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _create_engine(self):
        db_conf = self.config.get('database', {})
        user = db_conf.get('username', 'root')
        password = db_conf.get('password', '123456')
        host = db_conf.get('host', 'localhost')
        port = db_conf.get('port', 3306)
        dbname = db_conf.get('name', "sale")
        driver = db_conf.get('driver', 'mysql+pymysql')
        url = f"{driver}://{user}:{password}@{host}:{port}/{dbname}"
        return sqlalchemy.create_engine(url)

    def get_engine(self):
        """
        获取当前实例的引擎对象。

        Args:
            无

        Returns:
            engine (object): 引擎对象。

        """
        return self.engine

    def get_connection(self):
        """
        获取数据库连接。

        Args:
            无

        Returns:
            返回一个数据库连接对象。

        """
        return self.engine.connect()
    
    
class DatabaseManager:
    def __init__(self, config_path='configs/database.yaml'):
        """
        初始化方法，创建数据库连接引擎。

        Args:
            config_path (str, optional): 数据库配置文件的路径。默认为 'configs/database.yaml'。

        Returns:
            None
        """
        self.connector = DatabaseConnector(config_path)
        self.engine = self.connector.get_engine()

    def get_table_names(self):
        """
        获取数据库中的所有表名。

        Args:
            无

        Returns:
            List[str]: 包含所有表名的列表。
        """
        with self.engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            return [row[0] for row in result]

    def execute_query(self, query):
        """
        执行数据库查询并返回所有结果。

        Args:
            query (str): 要执行的SQL查询语句。

        Returns:
            list: 包含所有查询结果的列表，其中每个元素都是一个包含一行数据的元组。

        """
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()