#!/usr/bin/env python3
"""
异步文档总结API使用示例
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:11431"
API_ENDPOINT = f"{BASE_URL}/api/summarize/document-async"
STATUS_ENDPOINT = f"{BASE_URL}/api/summarize/status"

def submit_document_summary(tenant_id: int, url: str, file_type: int) -> dict:
    """
    提交文档总结任务
    
    Args:
        tenant_id: 租户ID
        url: 文档URL
        file_type: 文件类型 (0: txt, 1: 图片, 2: 表格, 3: ppt, 4: 视频, 5: pdf/docx)
    
    Returns:
        dict: 包含任务ID的响应数据
    """
    data = {
        "id": 12345,  # 这个ID不会被使用，实际会使用数据库生成的ID
        "tenant_id": tenant_id,
        "url": url,
        "file_type": file_type
    }
    
    print(f"提交任务: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(API_ENDPOINT, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"任务提交成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result["data"]
    else:
        print(f"任务提交失败: {response.status_code} - {response.text}")
        return None

def get_task_status(task_id: int, tenant_id: int) -> dict:
    """
    查询任务状态
    
    Args:
        task_id: 任务ID
        tenant_id: 租户ID
    
    Returns:
        dict: 任务状态信息
    """
    url = f"{STATUS_ENDPOINT}/{task_id}?tenant_id={tenant_id}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        return result["data"]
    else:
        print(f"查询状态失败: {response.status_code} - {response.text}")
        return None

def wait_for_completion(task_id: int, tenant_id: int, max_wait: int = 300) -> str:
    """
    等待任务完成
    
    Args:
        task_id: 任务ID
        tenant_id: 租户ID
        max_wait: 最大等待时间（秒）
    
    Returns:
        str: 总结结果
    """
    start_time = time.time()
    
    print(f"开始等待任务 {task_id} 完成...")
    
    while time.time() - start_time < max_wait:
        status_data = get_task_status(task_id, tenant_id)
        
        if status_data is None:
            print("无法获取任务状态")
            return None
        
        status = status_data["status"]
        print(f"任务状态: {status}")
        
        if status == 1:  # 已完成
            print("任务完成！")
            return status_data["ai_text"]
        elif status == 3:  # 处理失败
            print(f"任务处理失败: {status_data['ai_text']}")
            return None
        elif status == 2:  # 处理中
            print("任务正在处理中...")
        elif status == 0:  # 待处理
            print("任务等待处理中...")
        
        time.sleep(5)  # 等待5秒后再次查询
    
    print("任务超时")
    return None

def main():
    """主函数 - 演示完整的使用流程"""
    
    # 测试数据
    test_cases = [
        {
            "name": "文本文件总结",
            "tenant_id": 1,
            "url": "https://example.com/sample.txt",
            "file_type": 0
        },
        {
            "name": "图片文件总结",
            "tenant_id": 1,
            "url": "https://example.com/sample.jpg",
            "file_type": 1
        },
        {
            "name": "PDF文档总结",
            "tenant_id": 1,
            "url": "https://example.com/sample.pdf",
            "file_type": 5
        }
    ]
    
    print("=== 异步文档总结API使用示例 ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['name']}")
        print("-" * 50)
        
        # 提交任务
        task_data = submit_document_summary(
            test_case["tenant_id"],
            test_case["url"],
            test_case["file_type"]
        )
        
        if task_data is None:
            print("任务提交失败，跳过此测试\n")
            continue
        
        task_id = task_data["id"]
        tenant_id = task_data["tenant_id"]
        
        # 等待任务完成
        result = wait_for_completion(task_id, tenant_id)
        
        if result:
            print(f"总结结果: {result[:200]}..." if len(result) > 200 else f"总结结果: {result}")
        else:
            print("获取结果失败")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main() 