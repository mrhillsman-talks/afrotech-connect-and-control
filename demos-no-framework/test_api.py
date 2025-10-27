#!/usr/bin/env python3
"""Test the FastAPI endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_capabilities():
    print("2. Testing capabilities endpoint...")
    response = requests.get(f"{BASE_URL}/capabilities")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Tools: {len(data['tools'])}")
    print(f"   Resources: {len(data['resources'])}")
    print(f"   Prompts: {len(data['prompts'])}")
    print()

def test_users():
    print("3. Testing users endpoint...")
    response = requests.get(f"{BASE_URL}/users")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   User count: {data['count']}")
    if data['users']:
        print(f"   First user: {data['users'][0]['name']}")
    print()

def test_chat():
    print("4. Testing chat endpoint...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Hello! How are you?"}
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Response: {data['response'][:100]}...")
    print()

def test_chat_with_tool():
    print("5. Testing chat with tool call...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Create a random user"}
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Response: {data['response']}")
    if data.get('tool_calls'):
        print(f"   Tool calls: {len(data['tool_calls'])}")
        for call in data['tool_calls']:
            print(f"      - {call['tool']}: {call['result']}")
    print()

def test_tool_call():
    print("6. Testing direct tool call...")
    response = requests.post(
        f"{BASE_URL}/tools/call",
        json={
            "tool_name": "create-user",
            "arguments": {
                "name": "API Test User",
                "email": "apitest@test.com",
                "address": "123 API Street",
                "phone": "555-9999"
            }
        }
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Success: {data['success']}")
    print(f"   Result: {data['result']}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING MCP FASTAPI SERVER")
    print("=" * 60)
    print()

    try:
        test_health()
        test_capabilities()
        test_users()
        test_chat()
        test_chat_with_tool()
        test_tool_call()

        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
