#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web2MD 服务功能测试脚本

用于测试 Web2MD 服务的基本功能。
"""

import requests
import time
import sys


def test_service(base_url="http://localhost:8080"):
    """
    测试 Web2MD 服务功能
    
    Args:
        base_url (str): 服务基础 URL
    """
    print(f"🧪 开始测试 Web2MD 服务: {base_url}")
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False
    
    # 测试服务信息
    print("\n2. 测试服务信息...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ 服务信息获取成功")
        else:
            print(f"❌ 服务信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 服务信息获取异常: {str(e)}")
    
    # 测试无效请求
    print("\n3. 测试无效请求...")
    try:
        response = requests.get(f"{base_url}/target", timeout=10)
        if response.status_code == 400:
            print("✅ 无效请求处理正确")
        else:
            print(f"⚠️ 无效请求响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无效请求测试异常: {str(e)}")
    
    # 测试安全验证
    print("\n4. 测试安全验证...")
    try:
        response = requests.get(f"{base_url}/target?url=ftp://example.com", timeout=10)
        if response.status_code == 403:
            print("✅ 安全验证工作正常")
        else:
            print(f"⚠️ 安全验证响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 安全验证测试异常: {str(e)}")
    
    # 测试实际转换（使用白名单中的域名）
    print("\n5. 测试实际转换...")
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com"
    ]
    
    for url in test_urls:
        print(f"   测试 URL: {url}")
        try:
            response = requests.get(
                f"{base_url}/target?url={url}",
                timeout=60  # 转换可能需要更长时间
            )
            
            if response.status_code == 200:
                content = response.text
                if content and len(content) > 0:
                    print(f"   ✅ 转换成功，内容长度: {len(content)} 字符")
                    print(f"   📄 内容预览: {content[:100]}...")
                else:
                    print("   ⚠️ 转换成功但内容为空")
            elif response.status_code == 403:
                print("   ⚠️ 域名不在白名单中，请添加到白名单")
            else:
                print(f"   ❌ 转换失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
        
        except requests.exceptions.Timeout:
            print("   ⏰ 请求超时")
        except Exception as e:
            print(f"   ❌ 转换异常: {str(e)}")
        
        time.sleep(1)  # 避免请求过于频繁
    
    print("\n🎉 测试完成！")
    return True


def wait_for_service(base_url="http://localhost:5000", max_wait=30):
    """
    等待服务启动
    
    Args:
        base_url (str): 服务基础 URL
        max_wait (int): 最大等待时间（秒）
    """
    print(f"⏳ 等待服务启动: {base_url}")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 服务已启动")
                return True
        except:
            pass
        
        print(f"   等待中... ({i+1}/{max_wait})")
        time.sleep(1)
    
    print("❌ 服务启动超时")
    return False


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # 等待服务启动
    if wait_for_service(base_url):
        # 运行测试
        test_service(base_url)
    else:
        print("无法连接到服务，请确保服务正在运行")
        sys.exit(1)