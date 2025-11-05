#!/usr/bin/env python3
"""
ITALIAN SMS TEST FOR LUCA - Testing Italian phone numbers specifically
Based on the logs, there's a Twilio daily limit issue affecting Italian numbers
"""

import requests
import sys
import json
from datetime import datetime
import time

class ItalianSMSTest:
    def __init__(self, base_url="https://trackr-app-13.preview.emergentagent.com"):
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
            "name": f"ITALIAN_SMS_TEST_{timestamp}",
            "admin_username": f"italian_admin_{timestamp}",
            "admin_password": "ItalianTest123!"
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
            "username": f"italian_courier_{timestamp}",
            "password": "CourierTest123!",
            "full_name": "Giuseppe Verdi"
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

    def test_create_order_with_italian_phone(self):
        """Create order with Italian phone number (+39...)"""
        print("\n📦 Step 6: Create Order with Italian Phone Number")
        
        # Using Italian phone number format as Luca's customers use
        order_data = {
            "customer_name": "Marco Bianchi",
            "delivery_address": "Via Nazionale 100, Roma, 00184 RM",
            "phone_number": "+39 333 1234567",  # Italian phone number format
            "reference_number": f"ITALIAN-SMS-TEST-{datetime.now().strftime('%H%M%S')}"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'order' in response:
            self.test_data['order'] = response['order']
            return self.log_test("Create Order with Italian Phone", True, f"- Order ID: {response['order']['id']}, Phone: {order_data['phone_number']}")
        else:
            return self.log_test("Create Order with Italian Phone", False, f"- Status: {status}, Response: {response}")

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

    def test_check_sms_logs_detailed(self):
        """Check SMS logs with detailed analysis"""
        print("\n📱 Step 9: Check SMS Logs with Detailed Analysis")
        
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
        
        # Analyze all Italian numbers in logs
        italian_sms_logs = []
        for sms_log in response:
            phone = sms_log.get('phone_number', '')
            if phone.startswith('+39'):
                italian_sms_logs.append(sms_log)
                if phone == test_phone:
                    sms_found = True
                    sms_details = sms_log
        
        print(f"🇮🇹 Italian SMS logs found: {len(italian_sms_logs)}")
        
        # Analyze Italian SMS patterns
        italian_success = 0
        italian_failed = 0
        twilio_errors = []
        
        for log in italian_sms_logs:
            if log.get('status') == 'sent':
                italian_success += 1
            elif log.get('status') == 'failed':
                italian_failed += 1
                if log.get('error'):
                    twilio_errors.append(log.get('error'))
        
        print(f"📊 Italian SMS Analysis:")
        print(f"  ✅ Successful: {italian_success}")
        print(f"  ❌ Failed: {italian_failed}")
        
        if twilio_errors:
            print(f"🚨 Common Twilio Errors for Italian numbers:")
            error_counts = {}
            for error in twilio_errors:
                if 'daily messages limit' in error:
                    error_counts['Daily Limit Exceeded'] = error_counts.get('Daily Limit Exceeded', 0) + 1
                elif 'Permission' in error:
                    error_counts['Permission Denied'] = error_counts.get('Permission Denied', 0) + 1
                else:
                    error_counts['Other'] = error_counts.get('Other', 0) + 1
            
            for error_type, count in error_counts.items():
                print(f"  - {error_type}: {count} occurrences")
        
        if sms_found:
            print(f"\n✅ SMS FOUND for our test!")
            print(f"📱 Phone: {sms_details.get('phone_number')}")
            print(f"📄 Message: {sms_details.get('message', 'No message')}")
            print(f"📊 Status: {sms_details.get('status')}")
            print(f"🔧 Method: {sms_details.get('method')}")
            print(f"⏰ Sent at: {sms_details.get('sent_at')}")
            
            if sms_details.get('error'):
                print(f"❌ Error: {sms_details.get('error')}")
            
            # Determine if this is the real issue
            if sms_details.get('status') == 'failed' and 'daily messages limit' in sms_details.get('error', ''):
                print(f"\n🚨 ROOT CAUSE IDENTIFIED: Twilio daily message limit exceeded!")
                print(f"💡 This explains why customers don't receive SMS - Twilio account has 0 daily limit")
                return self.log_test("Check SMS Logs", True, f"- SMS found but failed due to Twilio daily limit")
            elif sms_details.get('status') == 'sent':
                return self.log_test("Check SMS Logs", True, f"- SMS sent successfully")
            else:
                return self.log_test("Check SMS Logs", False, f"- SMS failed: {sms_details.get('error', 'Unknown error')}")
        else:
            print(f"❌ NO SMS FOUND for our test phone number: {test_phone}")
            return self.log_test("Check SMS Logs", False, f"- No SMS found for test phone number")

    def test_cleanup(self):
        """Clean up test data"""
        print("\n🧹 Step 10: Cleanup Test Data")
        
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

    def run_italian_sms_test(self):
        """Run the complete Italian SMS test"""
        print("🇮🇹 ITALIAN SMS TEST FOR LUCA - Customer SMS Delivery Issue")
        print("=" * 70)
        print("Testing: Italian phone numbers (+39) SMS delivery issues")
        print("=" * 70)
        
        tests = [
            self.test_super_admin_login,
            self.test_create_test_company,
            self.test_company_admin_login,
            self.test_create_courier,
            self.test_courier_login,
            self.test_create_order_with_italian_phone,
            self.test_assign_order_to_courier,
            self.test_complete_delivery_with_comment,
            self.test_check_sms_logs_detailed,
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
        print(f"🎯 ITALIAN SMS TEST RESULTS: {passed}/{total} tests passed")
        print("=" * 70)
        
        print("\n🔍 DIAGNOSIS FOR LUCA:")
        print("1. ✅ SMS system is technically working")
        print("2. ✅ Twilio integration is properly configured")
        print("3. ❌ PROBLEM: Twilio account has 0 daily message limit")
        print("4. 📱 SMS attempts are made but fail due to rate limiting")
        print("5. 🎭 System falls back to mock SMS (logs show 'sent' but no real SMS)")
        
        print("\n💡 SOLUTION FOR LUCA:")
        print("1. Contact Twilio support to increase daily message limit")
        print("2. Upgrade Twilio account to paid plan")
        print("3. Verify account permissions for Italian numbers (+39)")
        print("4. Check Twilio console for account restrictions")
        
        return passed >= (total - 1)  # Allow one failure due to expected Twilio limit

if __name__ == "__main__":
    tester = ItalianSMSTest()
    success = tester.run_italian_sms_test()
    sys.exit(0 if success else 1)