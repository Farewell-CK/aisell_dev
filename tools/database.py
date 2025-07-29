import yaml
import os
import sqlalchemy
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

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
        driver = db_conf.get('driver', 'mysql+pymysql')
        
        # 根据驱动类型创建不同的连接URL
        if driver == 'sqlite':
            # SQLite配置
            database_path = db_conf.get('database_path', 'database/sale.db')
            # 确保目录存在
            db_dir = os.path.dirname(database_path)
            if db_dir:  # 只有当目录不为空时才创建
                os.makedirs(db_dir, exist_ok=True)
            url = f"sqlite:///{database_path}"
            
            # SQLite不需要复杂的连接池配置
            return sqlalchemy.create_engine(
                url,
                pool_size=1,
                max_overflow=0,
                pool_pre_ping=True
            )
        else:
            # MySQL配置
            user = db_conf.get('username', 'root')
            password = db_conf.get('password', '123456')
            host = db_conf.get('host', 'localhost')
            port = db_conf.get('port', 3306)
            dbname = db_conf.get('name', "sale")
            charset = db_conf.get('charset', 'utf8mb4')

            url = f"{driver}://{user}:{password}@{host}:{port}/{dbname}?charset={charset}"

            # ✅ 从配置中读取连接池参数
            pool_size = db_conf.get('pool_size', 5)
            max_overflow = db_conf.get('max_overflow', 10)
            pool_recycle = db_conf.get('pool_recycle', 3600)
            pool_pre_ping = db_conf.get('pool_pre_ping', True) # 默认开启
            pool_timeout = db_conf.get('pool_timeout', 30)
            connect_timeout = db_conf.get('connect_timeout', 10)

            # ✅ 将所有参数传入 create_engine
            return sqlalchemy.create_engine(
                url,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_recycle=pool_recycle,
                pool_pre_ping=pool_pre_ping,
                pool_timeout=pool_timeout,
                connect_args={'connect_timeout': connect_timeout}
            )

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
            result = connection.execute(text(query))
            formatted_results = []
            columns = result.keys() # 获取列名
            
            for row in result:
                # 将元组形式的行数据与列名打包成字典
                # row 是一个 Row 对象，它表现得像一个元组，也可以通过属性或索引访问
                # row._asdict() 是最方便的方式来将其转换为字典
                formatted_results.append(row._asdict())
            logging.info(f"查询数据成功: {formatted_results}")
            return formatted_results

    def execute_insert(self, query: str) -> int:
        """
        执行插入操作。

        Args:
            query (str): 完整的INSERT SQL语句
            params (dict, optional): SQL参数，用于参数化查询

        Returns:
            int: 插入操作影响的行数
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                connection.commit()
                logging.info(f"插入数据成功: {result}")
                return "插入成功"
        except Exception as e:
            logging.error(f"插入数据失败: {str(e)}")
            return str(e)

    def execute_update(self, query: str) -> int:
        """
        执行更新操作。

        Args:
            query (str): 完整的UPDATE SQL语句
        Returns:
            int: 更新操作影响的行数
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                connection.commit()
                logging.info(f"更新数据成功: {result}")
                return result.rowcount
        except Exception as e:
            logging.error(f"更新数据失败: {str(e)}")
            raise Exception(f"更新数据失败: {str(e)}")

    def execute_delete(self, query: str, params: dict = None) -> int:
        """
        执行删除操作。

        Args:
            query (str): 完整的DELETE SQL语句
            params (dict, optional): SQL参数，用于参数化查询

        Returns:
            int: 删除操作影响的行数
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                connection.commit()
                logging.info(f"删除数据成功: {result}")
                return result.rowcount
        except Exception as e:
            logging.error(f"删除数据失败: {str(e)}")
            raise Exception(f"删除数据失败: {str(e)}")

    def fetch_one(self, query: str, params: dict = None):
        """
        执行查询并返回单条记录。

        Args:
            query (str): 要执行的SQL查询语句
            params (dict, optional): SQL参数，用于参数化查询

        Returns:
            tuple: 包含单行数据的元组，如果没有找到记录则返回None
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                row = result.fetchone()
                if row:
                    logging.info(f"查询数据成功: {row}")
                    return tuple(row)  # 返回元组格式
                return None
        except Exception as e:
            logging.error(f"查询数据失败: {str(e)}")
            raise Exception(f"查询数据失败: {str(e)}")

    def fetch_all(self, query: str, params: dict = None):
        """
        执行查询并返回所有记录。

        Args:
            query (str): 要执行的SQL查询语句
            params (dict, optional): SQL参数，用于参数化查询

        Returns:
            list: 包含所有查询结果的列表，其中每个元素都是一个包含一行数据的元组
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                rows = result.fetchall()
                return [tuple(row) for row in rows]
        except Exception as e:
            raise Exception(f"查询数据失败: {str(e)}")