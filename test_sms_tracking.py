#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class SMSTrackingTester:
    def __init__(self, base_url="https://farmygo-delivery.preview.emergentagent.com"):
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, headers=headers)
            
            # Handle multiple expected status codes
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
            else:
                success = response.status_code == expected_status
            
            # Try to parse JSON, but handle non-JSON responses
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

    def setup_authentication(self):
        """Setup authentication tokens"""
        # Super Admin Login
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['super_admin'] = response['access_token']
            print("✅ Super Admin authentication setup")
            return True
        else:
            print(f"❌ Super Admin authentication failed: {status}")
            return False

    def test_sms_automatic_tracking_on_delivery(self):
        """Test automatic SMS tracking when delivery is completed"""
        print("\n🚚 Testing Automatic SMS Tracking on Delivery Completion")
        
        # Step 1: Create test company and courier for SMS tracking
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"SMS_Tracking_Company_{timestamp}",
            "admin_username": f"sms_track_admin_{timestamp}",
            "admin_password": "SMSTrack123!"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("SMS Automatic Tracking - Create Company", False, f"- Status: {status1}")
        
        track_company = response1['company']
        track_admin_creds = {
            'username': company_data['admin_username'],
            'password': company_data['admin_password']
        }
        
        # Login as company admin
        success2, status2, response2 = self.make_request(
            'POST', 'auth/login',
            data={"username": track_admin_creds['username'], "password": track_admin_creds['password']},
            expected_status=200
        )
        
        if not success2:
            return self.log_test("SMS Automatic Tracking - Admin Login", False, f"- Status: {status2}")
        
        track_admin_token = response2['access_token']
        
        # Create courier
        courier_data = {
            "username": f"sms_track_courier_{timestamp}",
            "password": "SMSTrackCourier123!",
            "full_name": f"SMS Tracker {timestamp}"
        }
        
        success3, status3, response3 = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=track_admin_token,
            expected_status=200
        )
        
        if not success3:
            return self.log_test("SMS Automatic Tracking - Create Courier", False, f"- Status: {status3}")
        
        # Get courier ID
        success4, status4, response4 = self.make_request(
            'GET', 'couriers',
            token=track_admin_token,
            expected_status=200
        )
        
        if not success4 or not response4:
            return self.log_test("SMS Automatic Tracking - Get Courier", False, f"- Status: {status4}")
        
        track_courier_id = response4[0]['id']
        
        # Login as courier
        success5, status5, response5 = self.make_request(
            'POST', 'auth/login',
            data={"username": courier_data['username'], "password": courier_data['password']},
            expected_status=200
        )
        
        if not success5:
            return self.log_test("SMS Automatic Tracking - Courier Login", False, f"- Status: {status5}")
        
        track_courier_token = response5['access_token']
        
        # Step 2: Get initial SMS statistics
        success6, status6, response6 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        initial_sms_count = 0
        if success6 and response6 and 'year_to_date' in response6:
            initial_sms_count = response6['year_to_date'].get('total_sms', 0)
        
        print(f"Initial SMS count: {initial_sms_count}")
        
        # Step 3: Create order with phone number
        order_data = {
            "customer_name": "SMS Tracking Test Customer",
            "delivery_address": "Via SMS Tracking 123, Roma, 00100 RM",
            "phone_number": "+39 333 7777777",  # Italian phone number
            "reference_number": f"SMS-TRACK-{timestamp}"
        }
        
        success7, status7, response7 = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=track_admin_token,
            expected_status=200
        )
        
        if not success7:
            return self.log_test("SMS Automatic Tracking - Create Order", False, f"- Status: {status7}")
        
        track_order = response7['order']
        
        # Step 4: Assign order to courier
        assign_data = {
            "order_id": track_order['id'],
            "courier_id": track_courier_id
        }
        
        success8, status8, response8 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=track_admin_token,
            expected_status=200
        )
        
        if not success8:
            return self.log_test("SMS Automatic Tracking - Assign Order", False, f"- Status: {status8}")
        
        # Step 5: Mark order as delivered (this should trigger SMS and update statistics)
        complete_data = {
            "order_id": track_order['id']
        }
        
        success9, status9, response9 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=track_courier_token,
            expected_status=200
        )
        
        if not success9:
            return self.log_test("SMS Automatic Tracking - Mark Delivered", False, f"- Status: {status9}")
        
        # Step 6: Wait a moment for SMS processing
        print("Waiting for SMS processing...")
        time.sleep(3)
        
        # Step 7: Check if SMS statistics were updated
        success10, status10, response10 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        sms_count_increased = False
        company_tracked = False
        new_sms_count = initial_sms_count
        
        if success10 and response10 and 'year_to_date' in response10:
            new_sms_count = response10['year_to_date'].get('total_sms', 0)
            sms_count_increased = new_sms_count > initial_sms_count
            
            # Check if company is tracked in breakdown
            if 'companies_breakdown' in response10:
                company_tracked = track_company['id'] in response10['companies_breakdown']
        
        print(f"New SMS count: {new_sms_count} (increased: {sms_count_increased})")
        
        # Step 8: Check SMS logs for the delivery notification
        success11, status11, response11 = self.make_request(
            'GET', 'sms-logs',
            token=track_admin_token,
            expected_status=200
        )
        
        sms_log_found = False
        correct_message = False
        if success11 and isinstance(response11, list):
            for log in response11:
                if (log.get('phone_number') == "+39 333 7777777" and 
                    log.get('company_id') == track_company['id']):
                    sms_log_found = True
                    message = log.get('message', '')
                    if 'SMS Tracking Test Customer' in message and 'completata con successo' in message:
                        correct_message = True
                    print(f"Found SMS log: {message[:100]}...")
                    break
        
        # Step 9: Cleanup - Delete test company
        delete_data = {"password": "admin123"}
        self.make_request(
            'DELETE', f'companies/{track_company["id"]}',
            data=delete_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        # Evaluate results
        overall_success = (success9 and sms_count_increased and company_tracked and 
                          sms_log_found and correct_message)
        
        if overall_success:
            return self.log_test("SMS Automatic Tracking on Delivery", True, 
                               f"- SMS sent ✅, Statistics updated ✅, Company tracked ✅, Message correct ✅")
        else:
            details = f"- Delivery marked: {success9}, SMS count increased: {sms_count_increased}, Company tracked: {company_tracked}, SMS log found: {sms_log_found}, Message correct: {correct_message}"
            return self.log_test("SMS Automatic Tracking on Delivery", False, details)

    def run_sms_tracking_tests(self):
        """Run SMS Tracking tests"""
        print("🚀 Starting SMS Tracking Tests")
        print("=" * 50)
        
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return False
        
        # Run SMS Tracking tests
        self.test_sms_automatic_tracking_on_delivery()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All SMS Tracking tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the issues above.")
            return False

def main():
    tester = SMSTrackingTester()
    success = tester.run_sms_tracking_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())