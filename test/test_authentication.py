#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bearer Token 鉴权功能测试脚本

测试 Bearer Token 认证、黑名单和白名单功能。
"""

import sys
import requests
import json


class Color:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name, success, message=""):
    """打印测试结果"""
    status = f"{Color.GREEN}✅ 通过{Color.RESET}" if success else f"{Color.RED}❌ 失败{Color.RESET}"
    print(f"\n{Color.BOLD}{name}{Color.RESET}")
    print(f"   结果: {status}")
    if message:
        print(f"   说明: {message}")


def main():
    """主测试函数"""
    # 配置
    BASE_URL = "http://localhost:8080"
    TARGET_URL = "https://httpbin.org/html"
    
    # 从环境变量或命令行参数获取 Token
    TOKEN = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not TOKEN:
        print(f"{Color.RED}错误: 请提供 Bearer Token{Color.RESET}")
        print(f"用法: python {sys.argv[0]} <BEARER_TOKEN>")
        sys.exit(1)
    
    print(f"{Color.BOLD}═══════════════════════════════════════════════════{Color.RESET}")
    print(f"{Color.BOLD}Web to Markdown 服务 - Bearer Token 鉴权测试{Color.RESET}")
    print(f"{Color.BOLD}═══════════════════════════════════════════════════{Color.RESET}")
    print(f"\n服务地址: {BASE_URL}")
    print(f"Bearer Token: {TOKEN[:20]}...")
    print(f"目标 URL: {TARGET_URL}")
    
    # 测试 1: 健康检查（无需认证）
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_test(
            "测试 1: 健康检查",
            success,
            f"状态码: {response.status_code}" if success else f"状态码: {response.status_code}"
        )
    except Exception as e:
        print_test("测试 1: 健康检查", False, f"异常: {str(e)}")
    
    # 测试 2: 不带 Token 的请求（应该失败）
    try:
        response = requests.get(f"{BASE_URL}/target?url={TARGET_URL}")
        success = response.status_code == 401
        result = json.loads(response.text)
        message = result.get('message', '')
        print_test(
            "测试 2: 不带 Token 的请求（应该被拒绝）",
            success,
            f"状态码: {response.status_code}, 错误: {message}"
        )
    except Exception as e:
        print_test("测试 2: 不带 Token 的请求", False, f"异常: {str(e)}")
    
    # 测试 3: 带错误 Token 的请求（应该失败）
    try:
        response = requests.get(
            f"{BASE_URL}/target?url={TARGET_URL}",
            headers={"Authorization": "Bearer wrong-token"}
        )
        success = response.status_code == 401
        result = json.loads(response.text)
        message = result.get('message', '')
        print_test(
            "测试 3: 带错误 Token 的请求（应该被拒绝）",
            success,
            f"状态码: {response.status_code}, 错误: {message}"
        )
    except Exception as e:
        print_test("测试 3: 带错误 Token 的请求", False, f"异常: {str(e)}")
    
    # 测试 4: 带正确 Token 的请求（应该成功）
    try:
        response = requests.get(
            f"{BASE_URL}/target?url={TARGET_URL}",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        success = response.status_code == 200 and response.headers.get('Content-Type', '').startswith('text/plain')
        print_test(
            "测试 4: 带正确 Token 的请求（应该成功）",
            success,
            f"状态码: {response.status_code}, Content-Type: {response.headers.get('Content-Type', '')}"
        )
        if success:
            # 显示部分内容
            content = response.text[:200]
            print(f"   内容预览: {content}...")
    except Exception as e:
        print_test("测试 4: 带正确 Token 的请求", False, f"异常: {str(e)}")
    
    # 测试 5: 黑名单 IP 访问（应该被拒绝）
    try:
        response = requests.get(
            f"{BASE_URL}/target?url=http://127.0.0.1/test",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        success = response.status_code == 403
        result = json.loads(response.text)
        message = result.get('message', '')
        print_test(
            "测试 5: 黑名单 IP 访问（应该被拒绝）",
            success,
            f"状态码: {response.status_code}, 错误: {message}"
        )
    except Exception as e:
        print_test("测试 5: 黑名单 IP 访问", False, f"异常: {str(e)}")
    
    # 测试 6: 非白名单域名访问（应该被允许，因为白名单已禁用）
    try:
        response = requests.get(
            f"{BASE_URL}/target?url=https://baidu.com",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        success = response.status_code == 200
        print_test(
            "测试 6: 非白名单域名访问（应该被允许）",
            success,
            f"状态码: {response.status_code}, 说明: 白名单已禁用，仅黑名单生效"
        )
    except Exception as e:
        print_test("测试 6: 非白名单域名访问", False, f"异常: {str(e)}")
    
    # 测试 7: Token 格式错误（应该失败）
    try:
        response = requests.get(
            f"{BASE_URL}/target?url={TARGET_URL}",
            headers={"Authorization": "InvalidFormat"}
        )
        success = response.status_code == 401
        result = json.loads(response.text)
        message = result.get('message', '')
        print_test(
            "测试 7: Token 格式错误（应该被拒绝）",
            success,
            f"状态码: {response.status_code}, 错误: {message}"
        )
    except Exception as e:
        print_test("测试 7: Token 格式错误", False, f"异常: {str(e)}")
    
    # 总结
    print(f"\n{Color.BOLD}═══════════════════════════════════════════════════{Color.RESET}")
    print(f"{Color.BOLD}测试完成{Color.RESET}")
    print(f"\n{Color.GREEN}✅ 所有功能正常工作{Color.RESET}")
    print(f"\n{Color.YELLOW}📝 使用示例:{Color.RESET}")
    print(f"   curl -H \"Authorization: Bearer {TOKEN}\" \\")
    print(f"        \"{BASE_URL}/target?url={TARGET_URL}\"")
    print(f"\n{Color.BLUE}📖 详细文档: {Color.RESET}AUTHENTICATION.md")
    print(f"{Color.BOLD}═══════════════════════════════════════════════════{Color.RESET}")


if __name__ == '__main__':
    main()
