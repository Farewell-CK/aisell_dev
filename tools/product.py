from core.database_core import db_manager
import logging

logger = logging.getLogger(__name__)

def get_product_by_task_id(task_id: int) -> dict:
    """
    根据任务ID查询产品信息
    
    Args:
        task_id (int): 任务ID
        
    Returns:
        dict: 包含状态和产品信息的字典
        {
            'status': bool,  # 查询是否成功
            'data': list     # 产品信息列表，如果查询失败则为None
        }
    """
    try:
        # 初始化数据库管理器
        
        # 首先查询sale_task_product表获取所有product_id
        task_product_query = f"""
            SELECT product_id 
            FROM sale_task_product 
            WHERE task_id = {task_id} 
            AND is_del = 0
        """
        task_product_result = db_manager.execute_query(task_product_query)
        logging.info(f"task_product_result: {task_product_result}")
        
        if not task_product_result:
            return {
                'status': False,
                'data': None
            }
            
        # 获取所有product_id
        product_ids = [str(row[0]) for row in task_product_result]
        
        # 根据product_ids查询sale_product表获取产品详细信息
        product_query = f"""
            SELECT 
                name,
                description,
                url,
                price_unit,
                sale_unit,
                standard_price,
                lowest_price,
                strategy
            FROM sale_product 
            WHERE id IN ({','.join(product_ids)})
            AND is_del = 0
        """
        product_result = db_manager.execute_query(product_query)
        
        if not product_result:
            return {
                'status': False,
                'data': None
            }
        """        # 定义字段名
        fields = [
            'name',
            'description',
            'url',
            'price_unit',
            'sale_unit',
            'standard_price',
            'lowest_price',
            'strategy'
        ]
        
        # 将查询结果转换为字典列表
        products_info = []
        for row in product_result:
            product_info = dict(zip(fields, row))
            products_info.append(product_info)
        """
        return {
            'status': True,
            'data': product_result
        }
        
    except Exception as e:
        return {
            'status': False,
            'data': None
        }
