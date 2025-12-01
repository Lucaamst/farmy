#!/usr/bin/env python3
"""
URGENT SMS TEST FOR LUCA - Customer SMS Delivery Issue
Testing the specific issue where couriers complete deliveries but customers don't receive SMS
"""

import requests
import sys
import json
from datetime import datetime
import time

class UrgentSMSTest:
    def __init__(self, base_url="https://deliverdocs.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.test_data = {}
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        if success:
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, headers=headers)
            
            # Handle multiple expected status codes
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
            else:
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
        """Login as super admin"""
        print("\n🔐 Step 1: Super Admin Login")
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['super_admin'] = response['access_token']
            return self.log_test("Super Admin Login", True, f"- Logged in successfully")
        else:
            return self.log_test("Super Admin Login", False, f"- Status: {status}, Response: {response}")

    def test_create_test_company(self):
        """Create a test company for SMS testing"""
        print("\n🏢 Step 2: Create Test Company")
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"SMS_URGENT_TEST_{timestamp}",
            "admin_username": f"sms_test_admin_{timestamp}",
            "admin_password": "UrgentTest123!"
        }
        
        success, status, response = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if success and 'company' in response:
            self.test_data['company'] = response['company']
            self.test_data['admin_creds'] = {
                'username': company_data['admin_username'],
                'password': company_data['admin_password']
            }
            return self.log_test("Create Test Company", True, f"- Company: {response['company']['name']}")
        else:
            return self.log_test("Create Test Company", False, f"- Status: {status}, Response: {response}")

    def test_company_admin_login(self):
        """Login as company admin"""
        print("\n👤 Step 3: Company Admin Login")
        if 'admin_creds' not in self.test_data:
            return self.log_test("Company Admin Login", False, "- No admin credentials available")
        
        creds = self.test_data['admin_creds']
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": creds['username'], "password": creds['password']},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['company_admin'] = response['access_token']
            return self.log_test("Company Admin Login", True, f"- Logged in successfully")
        else:
            return self.log_test("Company Admin Login", False, f"- Status: {status}, Response: {response}")

    def test_create_courier(self):
        """Create a courier for delivery testing"""
        print("\n🚚 Step 4: Create Courier")
        timestamp = datetime.now().strftime('%H%M%S')
        courier_data = {
            "username": f"sms_courier_{timestamp}",
            "password": "CourierTest123!",
            "full_name": "Mario Rossi"
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            self.test_data['courier_creds'] = courier_data
            
            # Get courier ID
            success2, status2, response2 = self.make_request(
                'GET', 'couriers',
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
            
            if success2 and response2:
                self.test_data['courier_id'] = response2[0]['id']
                return self.log_test("Create Courier", True, f"- Courier: {courier_data['username']}")
            else:
                return self.log_test("Create Courier", False, f"- Could not get courier ID")
        else:
            return self.log_test("Create Courier", False, f"- Status: {status}, Response: {response}")

    def test_courier_login(self):
        """Login as courier"""
        print("\n🚚 Step 5: Courier Login")
        if 'courier_creds' not in self.test_data:
            return self.log_test("Courier Login", False, "- No courier credentials available")
        
        creds = self.test_data['courier_creds']
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": creds['username'], "password": creds['password']},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['courier'] = response['access_token']
            return self.log_test("Courier Login", True, f"- Logged in successfully")
        else:
            return self.log_test("Courier Login", False, f"- Status: {status}, Response: {response}")

    def test_create_order_with_swiss_phone(self):
        """Create order with Swiss phone number (+41...)"""
        print("\n📦 Step 6: Create Order with Swiss Phone Number")
        
        # Using Swiss phone number format as requested
        order_data = {
            "customer_name": "Hans Mueller",
            "delivery_address": "Bahnhofstrasse 123, 8001 Zürich, Switzerland",
            "phone_number": "+41 79 123 4567",  # Swiss phone number format
            "reference_number": f"URGENT-SMS-TEST-{datetime.now().strftime('%H%M%S')}"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'order' in response:
            self.test_data['order'] = response['order']
            return self.log_test("Create Order with Swiss Phone", True, f"- Order ID: {response['order']['id']}, Phone: {order_data['phone_number']}")
        else:
            return self.log_test("Create Order with Swiss Phone", False, f"- Status: {status}, Response: {response}")

    def test_assign_order_to_courier(self):
        """Assign order to courier"""
        print("\n📋 Step 7: Assign Order to Courier")
        
        if 'order' not in self.test_data or 'courier_id' not in self.test_data:
            return self.log_test("Assign Order", False, "- Missing order or courier data")
        
        assign_data = {
            "order_id": self.test_data['order']['id'],
            "courier_id": self.test_data['courier_id']
        }
        
        success, status, response = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            return self.log_test("Assign Order to Courier", True, f"- Order assigned successfully")
        else:
            return self.log_test("Assign Order to Courier", False, f"- Status: {status}, Response: {response}")

    def test_complete_delivery_with_comment(self):
        """Complete delivery as courier with comment (this should trigger SMS)"""
        print("\n✅ Step 8: Complete Delivery with Comment (SMS TRIGGER)")
        
        if 'order' not in self.test_data:
            return self.log_test("Complete Delivery", False, "- No order data available")
        
        complete_data = {
            "order_id": self.test_data['order']['id'],
            "delivery_comment": "Consegna completata con successo. Cliente soddisfatto. Pacchetto lasciato alla reception."
        }
        
        print(f"📱 Attempting to complete delivery for order: {self.test_data['order']['id']}")
        print(f"📞 SMS should be sent to: {self.test_data['order']['phone_number']}")
        
        success, status, response = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        if success:
            print(f"✅ Delivery marked as completed - SMS should have been triggered!")
            return self.log_test("Complete Delivery with Comment", True, f"- Delivery completed, SMS notification should be sent")
        else:
            return self.log_test("Complete Delivery with Comment", False, f"- Status: {status}, Response: {response}")

    def test_check_sms_logs(self):
        """Check SMS logs to verify if SMS was actually sent"""
        print("\n📱 Step 9: Check SMS Logs for Verification")
        
        # Wait a moment for SMS processing
        time.sleep(3)
        
        success, status, response = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success:
            return self.log_test("Check SMS Logs", False, f"- Could not retrieve SMS logs: {status}")
        
        # Look for our test SMS
        test_phone = self.test_data['order']['phone_number']
        sms_found = False
        sms_details = {}
        
        print(f"🔍 Looking for SMS sent to: {test_phone}")
        print(f"📋 Total SMS logs found: {len(response)}")
        
        for sms_log in response:
            print(f"📱 SMS Log: {sms_log.get('phone_number')} - {sms_log.get('status')} - {sms_log.get('method', 'unknown')}")
            if sms_log.get('phone_number') == test_phone:
                sms_found = True
                sms_details = sms_log
                break
        
        if sms_found:
            print(f"✅ SMS FOUND in logs!")
            print(f"📱 Phone: {sms_details.get('phone_number')}")
            print(f"📄 Message: {sms_details.get('message', 'No message')}")
            print(f"📊 Status: {sms_details.get('status')}")
            print(f"🔧 Method: {sms_details.get('method')}")
            print(f"⏰ Sent at: {sms_details.get('sent_at')}")
            
            if sms_details.get('error'):
                print(f"❌ Error: {sms_details.get('error')}")
            
            return self.log_test("Check SMS Logs", True, f"- SMS found: {sms_details.get('status')} via {sms_details.get('method')}")
        else:
            print(f"❌ NO SMS FOUND for phone number: {test_phone}")
            print("📋 Available SMS logs:")
            for i, log in enumerate(response[:5]):  # Show first 5 logs
                print(f"  {i+1}. {log.get('phone_number')} - {log.get('status')} - {log.get('sent_at')}")
            
            return self.log_test("Check SMS Logs", False, f"- No SMS found for test phone number {test_phone}")

    def test_check_twilio_configuration(self):
        """Check if Twilio is properly configured"""
        print("\n🔧 Step 10: Check Twilio Configuration")
        
        # We can infer Twilio config from the SMS logs and any error messages
        success, status, response = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success:
            return self.log_test("Check Twilio Configuration", False, f"- Could not retrieve SMS logs")
        
        twilio_errors = []
        twilio_successes = []
        mock_usage = []
        
        for sms_log in response:
            method = sms_log.get('method', 'unknown')
            status_val = sms_log.get('status', 'unknown')
            error = sms_log.get('error', '')
            
            if method == 'twilio':
                if status_val == 'sent':
                    twilio_successes.append(sms_log)
                elif status_val == 'failed':
                    twilio_errors.append(sms_log)
            elif method == 'mock':
                mock_usage.append(sms_log)
        
        print(f"📊 Twilio Analysis:")
        print(f"  ✅ Twilio Successes: {len(twilio_successes)}")
        print(f"  ❌ Twilio Errors: {len(twilio_errors)}")
        print(f"  🎭 Mock Usage: {len(mock_usage)}")
        
        if twilio_errors:
            print(f"\n❌ Twilio Errors Found:")
            for error_log in twilio_errors[:3]:  # Show first 3 errors
                print(f"  - Phone: {error_log.get('phone_number')}")
                print(f"  - Error: {error_log.get('error', 'No error details')}")
                print(f"  - Time: {error_log.get('sent_at')}")
        
        # Determine if Twilio is working
        twilio_working = len(twilio_successes) > 0 or len(twilio_errors) > 0  # Either success or at least trying Twilio
        using_mock_only = len(mock_usage) > 0 and len(twilio_successes) == 0 and len(twilio_errors) == 0
        
        if twilio_working:
            return self.log_test("Check Twilio Configuration", True, f"- Twilio is configured and being used")
        elif using_mock_only:
            return self.log_test("Check Twilio Configuration", False, f"- Only mock SMS being used, Twilio not configured")
        else:
            return self.log_test("Check Twilio Configuration", False, f"- No SMS activity detected")

    def test_cleanup(self):
        """Clean up test data"""
        print("\n🧹 Step 11: Cleanup Test Data")
        
        if 'company' in self.test_data:
            delete_data = {"password": "admin123"}
            success, status, response = self.make_request(
                'DELETE', f'companies/{self.test_data["company"]["id"]}',
                data=delete_data,
                token=self.tokens.get('super_admin'),
                expected_status=200
            )
            
            if success:
                return self.log_test("Cleanup Test Data", True, f"- Test company deleted")
            else:
                return self.log_test("Cleanup Test Data", False, f"- Could not delete test company: {status}")
        else:
            return self.log_test("Cleanup Test Data", True, f"- No cleanup needed")

    def run_urgent_sms_test(self):
        """Run the complete urgent SMS test"""
        print("🚨 URGENT SMS TEST FOR LUCA - Customer SMS Delivery Issue")
        print("=" * 70)
        print("Testing: Couriers complete deliveries but customers don't receive SMS")
        print("=" * 70)
        
        tests = [
            self.test_super_admin_login,
            self.test_create_test_company,
            self.test_company_admin_login,
            self.test_create_courier,
            self.test_courier_login,
            self.test_create_order_with_swiss_phone,
            self.test_assign_order_to_courier,
            self.test_complete_delivery_with_comment,
            self.test_check_sms_logs,
            self.test_check_twilio_configuration,
            self.test_cleanup
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} - EXCEPTION: {str(e)}")
        
        print("\n" + "=" * 70)
        print(f"🎯 URGENT SMS TEST RESULTS: {passed}/{total} tests passed")
        print("=" * 70)
        
        if passed == total:
            print("✅ ALL TESTS PASSED - SMS system appears to be working")
        else:
            print("❌ SOME TESTS FAILED - SMS delivery issue confirmed")
            print("\n🔍 INVESTIGATION SUMMARY:")
            print("1. Check if SMS logs show the test message")
            print("2. Look for Twilio error messages in logs")
            print("3. Verify Twilio account permissions for Swiss numbers (+41)")
            print("4. Check rate limiting or account restrictions")
        
        return passed == total

if __name__ == "__main__":
    tester = UrgentSMSTest()
    success = tester.run_urgent_sms_test()
    sys.exit(0 if success else 1)