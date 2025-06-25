import asyncio
import json
from utils.opening_generator import OpeningGenerator, generate_opening

async def test_opening_generator():
    """测试开场白生成器"""
    
    # 初始化生成器
    generator = OpeningGenerator()
    
    # 测试数据
    customer_info = {
        "name": "李总",
        "company": "深圳智能科技有限公司",
        "position": "技术总监",
        "industry": "人工智能",
        "city": "深圳"
    }
    
    sales_info = {
        "name": "张三",
        "company": "东莞一路绿灯科技有限公司",
        "product": "大模型应用解决方案",
        "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
        "scenarios": "智能制造、金融风控、医疗诊断"
    }
    
    print("=== 开场白生成器测试 ===\n")
    
    # 1. 测试个性化开场白
    print("1. 个性化开场白:")
    result = await generator.generate_personalized_opening(
        customer_info, 
        sales_info, 
        context="通过LinkedIn了解到客户在AI部署方面有丰富经验"
    )
    print(f"状态: {result['status']}")
    print(f"类型: {result['type']}")
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    else:
        print(f"错误: {result['message']}")
    print()
    
    # 2. 测试行业针对性开场白
    print("2. 行业针对性开场白:")
    result = await generator.generate_industry_opening(
        "人工智能",
        sales_info,
        sales_info
    )
    print(f"状态: {result['status']}")
    print(f"类型: {result['type']}")
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    else:
        print(f"错误: {result['message']}")
    print()
    
    # 3. 测试事件开场白
    print("3. 事件开场白:")
    event_info = {
        "event_name": "2024深圳AI技术峰会",
        "event_time": "上周",
        "event_location": "深圳会展中心"
    }
    result = await generator.generate_event_opening(
        "展会",
        event_info,
        sales_info
    )
    print(f"状态: {result['status']}")
    print(f"类型: {result['type']}")
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    else:
        print(f"错误: {result['message']}")
    print()
    
    # 4. 测试推荐人开场白
    print("4. 推荐人开场白:")
    referrer_info = {
        "name": "王经理",
        "relationship": "合作伙伴"
    }
    result = await generator.generate_referral_opening(
        referrer_info,
        customer_info,
        sales_info
    )
    print(f"状态: {result['status']}")
    print(f"类型: {result['type']}")
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    else:
        print(f"错误: {result['message']}")
    print()
    
    # 5. 测试批量生成多种开场白
    print("5. 批量生成多种开场白:")
    result = await generator.generate_multiple_openings(
        customer_info,
        sales_info,
        opening_types=["personalized", "industry"]
    )
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        for i, opening in enumerate(result['openings'], 1):
            print(f"  开场白{i} ({opening['type']}): {opening.get('opening', opening.get('message', '生成失败'))}")
    print()
    
    # 6. 测试便捷函数
    print("6. 便捷函数测试:")
    result = await generate_opening(
        "personalized",
        customer_info,
        sales_info,
        context="客户在朋友圈分享了AI技术文章"
    )
    print(f"状态: {result['status']}")
    print(f"类型: {result['type']}")
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    else:
        print(f"错误: {result['message']}")

async def test_with_different_scenarios():
    """测试不同场景的开场白生成"""
    
    print("\n=== 不同场景测试 ===\n")
    
    # 场景1: 制造业客户
    manufacturing_customer = {
        "name": "陈总",
        "company": "东莞精密制造有限公司",
        "position": "生产总监",
        "industry": "制造业",
        "city": "东莞"
    }
    
    sales_info = {
        "name": "李四",
        "company": "东莞一路绿灯科技有限公司",
        "product": "智能质检解决方案",
        "advantage": "提升质检准确率95%，降低人工成本60%",
        "scenarios": "汽车零部件、电子产品、医疗器械"
    }
    
    print("场景1: 制造业客户")
    result = await generate_opening(
        "industry",
        manufacturing_customer,
        sales_info
    )
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    print()
    
    # 场景2: 金融行业客户
    finance_customer = {
        "name": "赵总",
        "company": "深圳金融科技公司",
        "position": "风控总监",
        "industry": "金融科技",
        "city": "深圳"
    }
    
    finance_sales_info = {
        "name": "王五",
        "company": "东莞一路绿灯科技有限公司",
        "product": "智能风控系统",
        "advantage": "实时风险评估，准确率提升40%",
        "scenarios": "银行、保险、证券"
    }
    
    print("场景2: 金融行业客户")
    result = await generate_opening(
        "industry",
        finance_customer,
        finance_sales_info
    )
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    print()
    
    # 场景3: 会议推荐
    print("场景3: 会议推荐")
    result = await generate_opening(
        "event",
        finance_customer,
        finance_sales_info,
        event_type="会议",
        event_info={
            "event_name": "金融科技峰会",
            "event_time": "昨天",
            "event_location": "深圳湾"
        }
    )
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_opening_generator())
    asyncio.run(test_with_different_scenarios()) 