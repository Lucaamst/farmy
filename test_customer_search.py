#!/usr/bin/env python3

import requests
import json

# Test customer search functionality
base_url = "https://ordersystem-2.preview.emergentagent.com"
api_url = f"{base_url}/api"

def test_customer_search():
    # First login as super admin
    login_response = requests.post(f"{api_url}/auth/login", json={
        "username": "superadmin",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print("❌ Super admin login failed")
        return False
    
    super_admin_token = login_response.json()['access_token']
    
    # Create a test company
    company_response = requests.post(f"{api_url}/companies", 
        json={
            "name": "TestSearchCompany",
            "admin_username": "searchadmin",
            "admin_password": "SearchPass123!"
        },
        headers={'Authorization': f'Bearer {super_admin_token}'}
    )
    
    if company_response.status_code != 200:
        print("❌ Company creation failed")
        return False
    
    # Login as company admin
    admin_login = requests.post(f"{api_url}/auth/login", json={
        "username": "searchadmin",
        "password": "SearchPass123!"
    })
    
    if admin_login.status_code != 200:
        print("❌ Company admin login failed")
        return False
    
    admin_token = admin_login.json()['access_token']
    
    # Create a test customer
    customer_response = requests.post(f"{api_url}/customers",
        json={
            "name": "Test Search Customer",
            "phone_number": "+39 333 1111111",
            "address": "Test Address"
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if customer_response.status_code != 200:
        print(f"❌ Customer creation failed: {customer_response.status_code} - {customer_response.text}")
        return False
    
    print("✅ Customer created successfully")
    
    # Test customer search
    search_response = requests.get(f"{api_url}/customers/search",
        params={"query": "Test"},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    print(f"Search response status: {search_response.status_code}")
    print(f"Search response: {search_response.text}")
    
    if search_response.status_code == 200:
        customers = search_response.json()
        print(f"✅ Customer search working - Found {len(customers)} customers")
        return True
    else:
        print(f"❌ Customer search failed: {search_response.status_code}")
        return False

if __name__ == "__main__":
    test_customer_search()