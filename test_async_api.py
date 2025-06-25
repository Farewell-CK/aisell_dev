import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:11431"

def test_async_document_summary():
    """测试异步文档总结API"""
    
    # 测试数据
    test_data = {
        "id": 12345,  # 这个ID不会被使用，实际会使用数据库生成的ID
        "tenant_id": 1,
        "url": "https://example.com/test.txt",
        "file_type": 0  # 0: txt
    }
    
    print("=== 测试异步文档总结API ===")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 发送异步请求
        response = requests.post(
            f"{BASE_URL}/api/summarize/document-async",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result["data"]["id"]
            tenant_id = result["data"]["tenant_id"]
            
            print(f"\n任务已提交，任务ID: {task_id}")
            print("等待5秒后查询任务状态...")
            time.sleep(5)
            
            # 查询任务状态
            status_response = requests.get(
                f"{BASE_URL}/api/summarize/status/{task_id}",
                params={"tenant_id": tenant_id}
            )
            
            print(f"状态查询响应: {json.dumps(status_response.json(), ensure_ascii=False, indent=2)}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_different_file_types():
    """测试不同文件类型"""
    
    test_cases = [
        {
            "name": "文本文件",
            "data": {
                "id": 1,
                "tenant_id": 1,
                "url": "https://example.com/test.txt",
                "file_type": 0
            }
        },
        {
            "name": "图片文件",
            "data": {
                "id": 2,
                "tenant_id": 1,
                "url": "https://example.com/test.jpg",
                "file_type": 1
            }
        },
        {
            "name": "表格文件",
            "data": {
                "id": 3,
                "tenant_id": 1,
                "url": "https://example.com/test.xlsx",
                "file_type": 2
            }
        },
        {
            "name": "PPT文件",
            "data": {
                "id": 4,
                "tenant_id": 1,
                "url": "https://example.com/test.pptx",
                "file_type": 3
            }
        },
        {
            "name": "视频文件",
            "data": {
                "id": 5,
                "tenant_id": 1,
                "url": "https://example.com/test.mp4",
                "file_type": 4
            }
        },
        {
            "name": "PDF文件",
            "data": {
                "id": 6,
                "tenant_id": 1,
                "url": "https://example.com/test.pdf",
                "file_type": 5
            }
        }
    ]
    
    print("\n=== 测试不同文件类型 ===")
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/summarize/document-async",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ 成功 - 任务ID: {result['data']['id']}")
            else:
                print(f"✗ 失败 - {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"✗ 异常: {str(e)}")

if __name__ == "__main__":
    # 测试基本功能
    test_async_document_summary()
    
    # 测试不同文件类型
    test_different_file_types() 