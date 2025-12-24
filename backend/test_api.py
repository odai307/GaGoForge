"""
Simple script to test API endpoints.
Run: python test_api.py
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_frameworks():
    """Test frameworks endpoint."""
    print("Testing /api/frameworks/")
    response = requests.get(f'{BASE_URL}/frameworks/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} frameworks")
        for fw in data:
            print(f"  - {fw['display_name']}")
    print()

def test_categories():
    """Test categories endpoint."""
    print("Testing /api/categories/")
    response = requests.get(f'{BASE_URL}/categories/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} categories")
    print()

def test_django_categories():
    """Test Django framework categories."""
    print("Testing /api/frameworks/django/categories/")
    response = requests.get(f'{BASE_URL}/frameworks/django/categories/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Django has {len(data)} categories:")
        for cat in data:
            print(f"  - {cat['display_name']}")
    print()

def test_framework_stats():
    """Test framework stats."""
    print("Testing /api/frameworks/django/stats/")
    response = requests.get(f'{BASE_URL}/frameworks/django/stats/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Django Statistics:")
        print(json.dumps(data, indent=2))
    print()

def test_problems():
    """Test problems endpoint."""
    print("Testing /api/problems/")
    response = requests.get(f'{BASE_URL}/problems/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} problems")
    print()

def test_problem_stats():
    """Test problem stats."""
    print("Testing /api/problems/stats/")
    response = requests.get(f'{BASE_URL}/problems/stats/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Problem Statistics:")
        print(json.dumps(data, indent=2))
    print()

def test_register():
    """Test user registration."""
    print("Testing user registration")
    response = requests.post(f'{BASE_URL}/users/register/', json={
        'username': 'apitest',
        'email': 'apitest@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'API',
        'last_name': 'Test'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("User created successfully!")
        print(f"Username: {data['user']['username']}")
        return data['tokens']['access']
    elif response.status_code == 400:
        print("User might already exist or validation error:")
        print(json.dumps(response.json(), indent=2))
    print()
    return None

def test_login():
    """Test user login."""
    print("Testing user login")
    response = requests.post(f'{BASE_URL}/auth/login/', json={
        'username': 'apitest',
        'password': 'testpass123'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Login successful!")
        return data['access']
    print()
    return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication."""
    headers = {'Authorization': f'Bearer {token}'}
    
    print("\nTesting authenticated endpoints...")
    
    # Test current user
    print("Testing /api/users/me/")
    response = requests.get(f'{BASE_URL}/users/me/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Current user: {data['username']}")
    print()
    
    # Test user profile
    print("Testing /api/users/profiles/me/")
    response = requests.get(f'{BASE_URL}/users/profiles/me/', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Profile loaded for: {data['username']}")
        print(f"Problems solved: {data['total_problems_solved']}")
    print()

if __name__ == '__main__':
    print("="*60)
    print("GaGoForge API Tests")
    print("="*60)
    print()
    
    # Test public endpoints
    test_frameworks()
    test_categories()
    test_django_categories()
    test_framework_stats()
    test_problems()
    test_problem_stats()
    
    # Test authentication
    token = test_register()
    if not token:
        token = test_login()
    
    if token:
        test_authenticated_endpoints(token)
    
    print("="*60)
    print("Tests completed!")
    print("="*60)