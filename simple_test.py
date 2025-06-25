import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_simple_opening():
    """简单的开场白生成测试"""
    try:
        from utils.opening_generator import OpeningGenerator
        
        print("=== 开场白生成器简单测试 ===\n")
        
        # 初始化生成器
        generator = OpeningGenerator()
        
        # 测试数据
        customer_info = {
            "name": "张总",
            "company": "深圳科技有限公司",
            "position": "技术总监",
            "industry": "人工智能",
            "city": "深圳"
        }
        
        sales_info = {
            "name": "李销售",
            "company": "东莞一路绿灯科技有限公司",
            "product": "大模型应用解决方案",
            "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
            "scenarios": "智能制造、金融风控、医疗诊断"
        }
        
        print("正在生成个性化开场白...")
        result = await generator.generate_personalized_opening(
            customer_info, 
            sales_info, 
            context="通过LinkedIn了解到客户在AI部署方面有丰富经验"
        )
        
        print(f"状态: {result['status']}")
        if result['status'] == 'success':
            print(f"开场白: {result['opening']}")
        else:
            print(f"错误: {result['message']}")
            
        print("\n测试完成！")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖包")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_opening()) 