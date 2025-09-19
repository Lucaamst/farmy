#!/usr/bin/env python3
"""
Test Twilio SMS Integration with US phone number to verify system works when permissions are correct
"""

import requests
import sys
import json
from datetime import datetime
import time

class TwilioUSTestTester:
    def __init__(self, base_url="https://ordersystem-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}

    def make_request(self, method, endpoint, data=None, token=None, expected_status=200, params=None):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": len(response.content),
                    "is_binary": True
                }
            
            return success, response.status_code, response_data
        
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_us_phone_sms(self):
        """Test SMS with US phone number"""
        print("🇺🇸 Testing SMS with US phone number...")
        
        # Login as super admin
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if not success:
            print(f"❌ Super admin login failed")
            return False
        
        super_admin_token = response['access_token']
        
        # Create test company
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"US_SMS_Test_{timestamp}",
            "admin_username": f"us_admin_{timestamp}",
            "admin_password": "USTest123!"
        }
        
        success, status, response = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=super_admin_token,
            expected_status=200
        )
        
        if not success:
            print(f"❌ Company creation failed")
            return False
        
        company = response['company']
        
        # Login as company admin
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": company_data['admin_username'], "password": company_data['admin_password']},
            expected_status=200
        )
        
        if not success:
            print(f"❌ Company admin login failed")
            return False
        
        admin_token = response['access_token']
        
        # Create courier
        courier_data = {
            "username": f"us_courier_{timestamp}",
            "password": "USCourier123!"
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=admin_token,
            expected_status=200
        )
        
        if not success:
            print(f"❌ Courier creation failed")
            return False
        
        # Get courier ID
        success, status, response = self.make_request(
            'GET', 'couriers',
            token=admin_token,
            expected_status=200
        )
        
        courier_id = response[0]['id']
        
        # Login as courier
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": courier_data['username'], "password": courier_data['password']},
            expected_status=200
        )
        
        if not success:
            print(f"❌ Courier login failed")
            return False
        
        courier_token = response['access_token']
        
        # Create order with US phone number
        order_data = {
            "customer_name": "John Smith",
            "delivery_address": "123 Main St, New York, NY 10001",
            "phone_number": "+1 555 123 4567",  # US phone number
            "reference_number": f"US-TEST-{timestamp}"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=admin_token,
            expected_status=200
        )
        
        if not success:
            print(f"❌ Order creation failed")
            return False
        
        order = response['order']
        
        # Assign order
        assign_data = {
            "order_id": order['id'],
            "courier_id": courier_id
        }
        
        success, status, response = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=admin_token,
            expected_status=200
        )
        
        if not success:
            print(f"❌ Order assignment failed")
            return False
        
        # Mark as delivered
        complete_data = {
            "order_id": order['id']
        }
        
        success, status, response = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=courier_token,
            expected_status=200
        )
        
        if not success:
            print(f"❌ Mark delivered failed")
            return False
        
        print(f"✅ Order marked as delivered for US number")
        
        # Wait and check SMS logs
        time.sleep(3)
        
        success, status, response = self.make_request(
            'GET', 'sms-logs',
            token=admin_token,
            expected_status=200
        )
        
        if success:
            for sms_log in response:
                if sms_log.get('phone_number') == "+1 555 123 4567":
                    print(f"📱 SMS Log found:")
                    print(f"   Phone: {sms_log.get('phone_number')}")
                    print(f"   Method: {sms_log.get('method')}")
                    print(f"   Status: {sms_log.get('status')}")
                    print(f"   Message: {sms_log.get('message')}")
                    if sms_log.get('error'):
                        print(f"   Error: {sms_log.get('error')}")
                    break
        
        # Cleanup
        delete_data = {"password": "admin123"}
        self.make_request(
            'DELETE', f'companies/{company["id"]}',
            data=delete_data,
            token=super_admin_token,
            expected_status=200
        )
        
        return True

def main():
    tester = TwilioUSTestTester()
    tester.test_us_phone_sms()

if __name__ == "__main__":
    main()