import requests
import sys
import json
from datetime import datetime

class DeliveryManagementAPITester:
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

    def make_request(self, method, endpoint, data=None, token=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            return success, response.status_code, response.json() if response.content else {}
        
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_super_admin_login(self):
        """Test super admin login"""
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['super_admin'] = response['access_token']
            self.test_data['super_admin_user'] = response['user']
            return self.log_test("Super Admin Login", True, f"- Token received")
        else:
            return self.log_test("Super Admin Login", False, f"- Status: {status}, Response: {response}")

    def test_create_company(self):
        """Test creating a company with admin"""
        company_data = {
            "name": f"TestCompany_{datetime.now().strftime('%H%M%S')}",
            "admin_username": f"testadmin_{datetime.now().strftime('%H%M%S')}",
            "admin_password": "testpass123"
        }
        
        success, status, response = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if success and 'company' in response:
            self.test_data['company'] = response['company']
            self.test_data['company_admin_creds'] = {
                'username': company_data['admin_username'],
                'password': company_data['admin_password']
            }
            return self.log_test("Create Company", True, f"- Company: {response['company']['name']}")
        else:
            return self.log_test("Create Company", False, f"- Status: {status}, Response: {response}")

    def test_get_companies(self):
        """Test getting companies list"""
        success, status, response = self.make_request(
            'GET', 'companies',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            return self.log_test("Get Companies", True, f"- Found {len(response)} companies")
        else:
            return self.log_test("Get Companies", False, f"- Status: {status}, Response: {response}")

    def test_company_admin_login(self):
        """Test company admin login"""
        if 'company_admin_creds' not in self.test_data:
            return self.log_test("Company Admin Login", False, "- No company admin credentials available")
        
        creds = self.test_data['company_admin_creds']
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": creds['username'], "password": creds['password']},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['company_admin'] = response['access_token']
            self.test_data['company_admin_user'] = response['user']
            return self.log_test("Company Admin Login", True, f"- Token received")
        else:
            return self.log_test("Company Admin Login", False, f"- Status: {status}, Response: {response}")

    def test_create_courier(self):
        """Test creating a courier"""
        courier_data = {
            "username": f"testcourier_{datetime.now().strftime('%H%M%S')}",
            "password": "courierpass123"
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            self.test_data['courier_creds'] = courier_data
            return self.log_test("Create Courier", True, f"- Courier: {courier_data['username']}")
        else:
            return self.log_test("Create Courier", False, f"- Status: {status}, Response: {response}")

    def test_get_couriers(self):
        """Test getting couriers list"""
        success, status, response = self.make_request(
            'GET', 'couriers',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            if response:
                self.test_data['courier_id'] = response[0]['id']
            return self.log_test("Get Couriers", True, f"- Found {len(response)} couriers")
        else:
            return self.log_test("Get Couriers", False, f"- Status: {status}, Response: {response}")

    def test_create_order(self):
        """Test creating a delivery order"""
        order_data = {
            "customer_name": "John Doe",
            "delivery_address": "123 Test Street, Test City",
            "phone_number": "+1234567890"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'order' in response:
            self.test_data['order'] = response['order']
            return self.log_test("Create Order", True, f"- Order ID: {response['order']['id']}")
        else:
            return self.log_test("Create Order", False, f"- Status: {status}, Response: {response}")

    def test_get_orders(self):
        """Test getting orders list"""
        success, status, response = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            return self.log_test("Get Orders", True, f"- Found {len(response)} orders")
        else:
            return self.log_test("Get Orders", False, f"- Status: {status}, Response: {response}")

    def test_assign_order(self):
        """Test assigning order to courier"""
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
            return self.log_test("Assign Order", True, "- Order assigned to courier")
        else:
            return self.log_test("Assign Order", False, f"- Status: {status}, Response: {response}")

    def test_courier_login(self):
        """Test courier login"""
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
            self.test_data['courier_user'] = response['user']
            return self.log_test("Courier Login", True, f"- Token received")
        else:
            return self.log_test("Courier Login", False, f"- Status: {status}, Response: {response}")

    def test_get_courier_deliveries(self):
        """Test getting courier's assigned deliveries"""
        success, status, response = self.make_request(
            'GET', 'courier/deliveries',
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            return self.log_test("Get Courier Deliveries", True, f"- Found {len(response)} deliveries")
        else:
            return self.log_test("Get Courier Deliveries", False, f"- Status: {status}, Response: {response}")

    def test_mark_delivery_completed(self):
        """Test marking delivery as completed (triggers SMS)"""
        if 'order' not in self.test_data:
            return self.log_test("Mark Delivery Completed", False, "- No order data available")
        
        complete_data = {
            "order_id": self.test_data['order']['id']
        }
        
        success, status, response = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        if success:
            return self.log_test("Mark Delivery Completed", True, "- SMS notification should be triggered")
        else:
            return self.log_test("Mark Delivery Completed", False, f"- Status: {status}, Response: {response}")

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Delivery Management API Tests")
        print("=" * 50)
        
        # Phase 1: Authentication & Super Admin Tests
        print("\n📋 Phase 1: Authentication & Super Admin Tests")
        self.test_super_admin_login()
        self.test_create_company()
        self.test_get_companies()
        
        # Phase 2: Company Admin Tests
        print("\n📋 Phase 2: Company Admin Tests")
        self.test_company_admin_login()
        self.test_create_courier()
        self.test_get_couriers()
        self.test_create_order()
        self.test_get_orders()
        self.test_assign_order()
        
        # Phase 3: Courier Tests
        print("\n📋 Phase 3: Courier Tests")
        self.test_courier_login()
        self.test_get_courier_deliveries()
        self.test_mark_delivery_completed()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the issues above.")
            return False

def main():
    tester = DeliveryManagementAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())