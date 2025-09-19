#!/usr/bin/env python3
"""
Focused Twilio SMS Integration Test for FarmyGo Delivery Management System
Tests the SMS notification system with real Twilio integration using Italian phone numbers
"""

import requests
import sys
import json
from datetime import datetime
import time

class TwilioSMSIntegrationTester:
    def __init__(self, base_url="https://ordersystem-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.test_data = {}
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

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

    def test_super_admin_login(self):
        """Test super admin login to get token"""
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['super_admin'] = response['access_token']
            return self.log_test("Super Admin Login", True, f"- Token received")
        else:
            return self.log_test("Super Admin Login", False, f"- Status: {status}, Response: {response}")

    def test_twilio_sms_integration_complete(self):
        """Complete Twilio SMS integration test with Italian phone number"""
        print("\n🔔 COMPREHENSIVE TWILIO SMS INTEGRATION TEST")
        print("=" * 60)
        
        # Step 1: Create a test company and courier for SMS testing
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"SMS_Test_Company_{timestamp}",
            "admin_username": f"sms_admin_{timestamp}",
            "admin_password": "SMSTest123!"
        }
        
        print(f"📋 Step 1: Creating test company '{company_data['name']}'...")
        success1, status1, response1 = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("SMS Test - Create Company", False, f"- Status: {status1}, Response: {response1}")
        
        sms_company = response1['company']
        sms_admin_creds = {
            'username': company_data['admin_username'],
            'password': company_data['admin_password']
        }
        print(f"✅ Company created: {sms_company['name']} (ID: {sms_company['id']})")
        
        # Step 2: Login as company admin
        print(f"📋 Step 2: Logging in as company admin...")
        success2, status2, response2 = self.make_request(
            'POST', 'auth/login',
            data={"username": sms_admin_creds['username'], "password": sms_admin_creds['password']},
            expected_status=200
        )
        
        if not success2:
            return self.log_test("SMS Test - Admin Login", False, f"- Status: {status2}, Response: {response2}")
        
        sms_admin_token = response2['access_token']
        print(f"✅ Company admin logged in successfully")
        
        # Step 3: Create a courier for SMS testing
        courier_data = {
            "username": f"sms_courier_{timestamp}",
            "password": "SMSCourier123!"
        }
        
        print(f"📋 Step 3: Creating courier '{courier_data['username']}'...")
        success3, status3, response3 = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success3:
            return self.log_test("SMS Test - Create Courier", False, f"- Status: {status3}, Response: {response3}")
        
        # Get courier ID
        success4, status4, response4 = self.make_request(
            'GET', 'couriers',
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success4 or not response4:
            return self.log_test("SMS Test - Get Courier", False, f"- Status: {status4}")
        
        sms_courier_id = response4[0]['id']
        print(f"✅ Courier created: {courier_data['username']} (ID: {sms_courier_id})")
        
        # Step 4: Login as courier
        print(f"📋 Step 4: Logging in as courier...")
        success5, status5, response5 = self.make_request(
            'POST', 'auth/login',
            data={"username": courier_data['username'], "password": courier_data['password']},
            expected_status=200
        )
        
        if not success5:
            return self.log_test("SMS Test - Courier Login", False, f"- Status: {status5}, Response: {response5}")
        
        sms_courier_token = response5['access_token']
        print(f"✅ Courier logged in successfully")
        
        # Step 5: Create a test order with Italian phone number
        order_data = {
            "customer_name": "Marco Bianchi",
            "delivery_address": "Via Nazionale 100, Roma, 00184 RM",
            "phone_number": "+39 333 1234567",  # Italian phone number format as requested
            "reference_number": f"SMS-TEST-{timestamp}"
        }
        
        print(f"📋 Step 5: Creating order for {order_data['customer_name']} with phone {order_data['phone_number']}...")
        success6, status6, response6 = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success6:
            return self.log_test("SMS Test - Create Order", False, f"- Status: {status6}, Response: {response6}")
        
        sms_order = response6['order']
        print(f"✅ Order created: {sms_order['id']} for {order_data['customer_name']}")
        
        # Step 6: Assign order to courier
        assign_data = {
            "order_id": sms_order['id'],
            "courier_id": sms_courier_id
        }
        
        print(f"📋 Step 6: Assigning order to courier...")
        success7, status7, response7 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success7:
            return self.log_test("SMS Test - Assign Order", False, f"- Status: {status7}, Response: {response7}")
        
        print(f"✅ Order assigned to courier")
        
        # Step 7: Mark order as delivered (this should trigger Twilio SMS)
        complete_data = {
            "order_id": sms_order['id']
        }
        
        print(f"📋 Step 7: Marking order as delivered (triggering SMS)...")
        success8, status8, response8 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=sms_courier_token,
            expected_status=200
        )
        
        if not success8:
            return self.log_test("SMS Test - Mark Delivered", False, f"- Status: {status8}, Response: {response8}")
        
        print(f"✅ Order marked as delivered - SMS should be triggered")
        
        # Step 8: Wait and check SMS logs to verify SMS was sent via Twilio
        print(f"📋 Step 8: Waiting 3 seconds for SMS processing...")
        time.sleep(3)
        
        print(f"📋 Step 9: Checking SMS logs...")
        success9, status9, response9 = self.make_request(
            'GET', 'sms-logs',
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success9:
            return self.log_test("SMS Test - Get SMS Logs", False, f"- Status: {status9}, Response: {response9}")
        
        # Step 9: Verify SMS log contains our test with correct details
        sms_found = False
        twilio_used = False
        italian_message = False
        correct_phone = False
        sms_details = {}
        
        print(f"📋 Step 10: Analyzing SMS logs...")
        print(f"Found {len(response9)} SMS log entries")
        
        for i, sms_log in enumerate(response9):
            print(f"SMS Log {i+1}: Phone: {sms_log.get('phone_number')}, Method: {sms_log.get('method')}, Status: {sms_log.get('status')}")
            
            if sms_log.get('phone_number') == "+39 333 1234567":
                sms_found = True
                sms_details = sms_log
                correct_phone = True
                
                if sms_log.get('method') == 'twilio':
                    twilio_used = True
                    print(f"✅ Found SMS sent via Twilio")
                else:
                    print(f"⚠️  SMS found but method is: {sms_log.get('method')}")
                
                message = sms_log.get('message', '')
                if 'Ciao Marco Bianchi!' in message and 'FarmyGo' in message and 'Via Nazionale 100' in message:
                    italian_message = True
                    print(f"✅ Italian message format correct")
                    print(f"Message: {message}")
                else:
                    print(f"⚠️  Message format incorrect: {message}")
                break
        
        # Step 10: Cleanup - Delete test company
        print(f"📋 Step 11: Cleaning up test company...")
        delete_data = {"password": "admin123"}
        cleanup_success, _, _ = self.make_request(
            'DELETE', f'companies/{sms_company["id"]}',
            data=delete_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if cleanup_success:
            print(f"✅ Test company cleaned up")
        else:
            print(f"⚠️  Failed to cleanup test company")
        
        # Final evaluation
        print(f"\n📊 SMS INTEGRATION TEST RESULTS:")
        print(f"- SMS Found: {'✅' if sms_found else '❌'}")
        print(f"- Correct Phone Number: {'✅' if correct_phone else '❌'}")
        print(f"- Twilio Used (not mock): {'✅' if twilio_used else '❌'}")
        print(f"- Italian Message Format: {'✅' if italian_message else '❌'}")
        
        if sms_found and twilio_used and italian_message and correct_phone:
            return self.log_test("Twilio SMS Integration - COMPLETE TEST", True, 
                               f"- SMS sent via Twilio with Italian message to +39 333 1234567")
        elif sms_found and not twilio_used:
            return self.log_test("Twilio SMS Integration - COMPLETE TEST", False, 
                               f"- SMS found but used '{sms_details.get('method')}' instead of Twilio")
        elif sms_found and not italian_message:
            return self.log_test("Twilio SMS Integration - COMPLETE TEST", False, 
                               f"- SMS sent but Italian message format incorrect")
        else:
            return self.log_test("Twilio SMS Integration - COMPLETE TEST", False, 
                               f"- No SMS log found for test phone number +39 333 1234567")

    def run_twilio_sms_test(self):
        """Run focused Twilio SMS integration test"""
        print("🚀 TWILIO SMS INTEGRATION TEST FOR FARMYGO")
        print("Testing SMS notifications with Italian phone numbers")
        print("=" * 70)
        
        # Login as super admin first
        if not self.test_super_admin_login():
            print("❌ Cannot proceed without super admin access")
            return False
        
        # Run the comprehensive SMS test
        success = self.test_twilio_sms_integration_complete()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 SMS Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if success:
            print("🎉 Twilio SMS Integration test PASSED!")
            print("✅ SMS notifications are working with real Twilio service")
            print("✅ Italian message format is correct")
            print("✅ Italian phone number format (+39 333 1234567) works")
        else:
            print("⚠️  Twilio SMS Integration test FAILED!")
            print("❌ Check the issues above for details")
        
        return success

def main():
    tester = TwilioSMSIntegrationTester()
    success = tester.run_twilio_sms_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())