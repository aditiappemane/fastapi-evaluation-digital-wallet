"""Test script for Digital Wallet API"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_user():
    """Test user creation"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "phone_number": "1234567890",
        "initial_balance": 100.0
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Create user: {response.status_code}")
    if response.status_code == 200:
        print(f"User created: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_user():
    """Test getting a user"""
    response = requests.get(f"{BASE_URL}/users/1")
    print(f"Get user: {response.status_code}")
    if response.status_code == 200:
        print(f"User: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_balance():
    """Test getting user balance"""
    response = requests.get(f"{BASE_URL}/wallet/1/balance")
    print(f"Get balance: {response.status_code}")
    if response.status_code == 200:
        print(f"Balance: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("Testing Digital Wallet API...")
    print("=" * 50)
    
    test_root()
    test_create_user()
    test_get_user()
    test_get_balance()
