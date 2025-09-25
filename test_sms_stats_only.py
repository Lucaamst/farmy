#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class SMSStatsAPITester:
    def __init__(self, base_url="https://farmygo-delivery.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
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

    def test_sms_statistics_api_access(self):
        """Test SMS statistics API access and authentication"""
        print("\n📊 Testing SMS Statistics API Access")
        
        # Test 1: Super Admin can access SMS stats
        success1, status1, response1 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        # Verify response format for super admin
        format_correct = True
        if success1 and response1:
            required_fields = ['current_month', 'monthly_history', 'year_to_date', 'cost_settings', 'companies_breakdown']
            format_correct = all(field in response1 for field in required_fields)
            
            # Check year_to_date structure
            if 'year_to_date' in response1:
                ytd_fields = ['total_sms', 'total_cost', 'success_rate']
                ytd_correct = all(field in response1['year_to_date'] for field in ytd_fields)
                format_correct = format_correct and ytd_correct
        else:
            format_correct = False
        
        if success1 and format_correct:
            return self.log_test("SMS Statistics API Access", True, f"- Super Admin access ✅, Format correct ✅")
        else:
            details = f"- Super Admin: {success1} ({status1}), Format: {format_correct}"
            return self.log_test("SMS Statistics API Access", False, details)

    def test_sms_cost_settings_api(self):
        """Test SMS cost settings update API"""
        print("\n💰 Testing SMS Cost Settings API")
        
        # Test 1: Get initial cost settings (via stats API)
        success1, status1, response1 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        initial_cost = 0.05  # Default cost
        if success1 and response1 and 'cost_settings' in response1:
            initial_cost = response1['cost_settings'].get('cost_per_sms', 0.05)
        
        # Test 2: Update SMS cost settings with valid data
        new_cost_data = {
            "cost_per_sms": 0.08,
            "currency": "EUR"
        }
        
        success2, status2, response2 = self.make_request(
            'PUT', 'super-admin/sms-cost-settings',
            data=new_cost_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        # Test 3: Verify settings were updated
        success3, status3, response3 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        settings_updated = False
        if success3 and response3 and 'cost_settings' in response3:
            updated_cost = response3['cost_settings'].get('cost_per_sms')
            settings_updated = updated_cost == 0.08
        
        # Test 4: Try to update with negative cost (should fail)
        invalid_cost_data = {
            "cost_per_sms": -0.01,
            "currency": "EUR"
        }
        
        success4, status4, response4 = self.make_request(
            'PUT', 'super-admin/sms-cost-settings',
            data=invalid_cost_data,
            token=self.tokens.get('super_admin'),
            expected_status=400
        )
        
        # Test 5: Restore original cost settings
        restore_data = {
            "cost_per_sms": initial_cost,
            "currency": "EUR"
        }
        
        success5, status5, response5 = self.make_request(
            'PUT', 'super-admin/sms-cost-settings',
            data=restore_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        overall_success = success1 and success2 and success3 and settings_updated and success4 and success5
        
        if overall_success:
            return self.log_test("SMS Cost Settings API", True, f"- Update ✅, Validation ✅, Restore ✅")
        else:
            details = f"- Get initial: {success1}, Update: {success2}, Verify: {success3}, Updated: {settings_updated}, Negative rejected: {success4}, Restore: {success5}"
            return self.log_test("SMS Cost Settings API", False, details)

    def test_sms_monthly_report_api(self):
        """Test SMS monthly report API"""
        print("\n📅 Testing SMS Monthly Report API")
        
        from datetime import datetime
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Test 1: Get current month report (may be empty initially)
        success1, status1, response1 = self.make_request(
            'GET', 'super-admin/sms-monthly-report',
            params={"year": current_year, "month": current_month},
            token=self.tokens.get('super_admin'),
            expected_status=[200, 404]  # 404 if no data exists yet
        )
        
        # Test 2: Get report for non-existent month (should return 404)
        success2, status2, response2 = self.make_request(
            'GET', 'super-admin/sms-monthly-report',
            params={"year": 2020, "month": 1},  # Old date unlikely to have data
            token=self.tokens.get('super_admin'),
            expected_status=404
        )
        
        # Verify response format if data exists
        format_correct = True
        if success1 and status1 == 200 and response1:
            required_fields = ['monthly_stats', 'daily_breakdown', 'period']
            format_correct = all(field in response1 for field in required_fields)
        
        overall_success = success1 and success2 and format_correct
        
        if overall_success:
            data_status = "with data" if status1 == 200 else "no data (expected)"
            return self.log_test("SMS Monthly Report API", True, f"- Current month {data_status} ✅, Non-existent month 404 ✅, Format ✅")
        else:
            details = f"- Current month: {success1} ({status1}), Non-existent: {success2}, Format: {format_correct}"
            return self.log_test("SMS Monthly Report API", False, details)

    def run_sms_stats_tests(self):
        """Run SMS Statistics API tests"""
        print("🚀 Starting SMS Statistics API Tests")
        print("=" * 50)
        
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return False
        
        # Run SMS Statistics API tests
        self.test_sms_statistics_api_access()
        self.test_sms_cost_settings_api()
        self.test_sms_monthly_report_api()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All SMS Statistics API tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the issues above.")
            return False

def main():
    tester = SMSStatsAPITester()
    success = tester.run_sms_stats_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())