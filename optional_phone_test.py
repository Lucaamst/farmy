import requests
import sys
import json
from datetime import datetime
import time

class OptionalPhoneNumberTester:
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

    def setup_test_environment(self):
        """Setup test company, admin, and courier for testing"""
        print("🔧 Setting up test environment...")
        
        # Login as super admin
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to login as super admin: {status}, {response}")
            return False
        
        self.tokens['super_admin'] = response['access_token']
        
        # Create test company
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"OptionalPhone_TestCompany_{timestamp}",
            "admin_username": f"phone_admin_{timestamp}",
            "admin_password": "PhoneTest123!"
        }
        
        success, status, response = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens['super_admin'],
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to create test company: {status}, {response}")
            return False
        
        self.test_data['company'] = response['company']
        self.test_data['admin_creds'] = {
            'username': company_data['admin_username'],
            'password': company_data['admin_password']
        }
        
        # Login as company admin
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data=self.test_data['admin_creds'],
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to login as company admin: {status}, {response}")
            return False
        
        self.tokens['company_admin'] = response['access_token']
        
        # Create test courier
        courier_data = {
            "username": f"phone_courier_{timestamp}",
            "password": "PhoneCourier123!"
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to create courier: {status}, {response}")
            return False
        
        # Get courier ID
        success, status, response = self.make_request(
            'GET', 'couriers',
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success or not response:
            print(f"❌ Failed to get courier list: {status}")
            return False
        
        self.test_data['courier_id'] = response[0]['id']
        self.test_data['courier_creds'] = courier_data
        
        # Login as courier
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data=courier_data,
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to login as courier: {status}, {response}")
            return False
        
        self.tokens['courier'] = response['access_token']
        
        print("✅ Test environment setup complete")
        return True

    def test_create_order_without_phone(self):
        """Test creating order WITHOUT phone number"""
        order_data = {
            "customer_name": "Giovanni Rossi",
            "delivery_address": "Via Milano 123, Torino, 10100 TO",
            "reference_number": "NO-PHONE-001"
            # Note: phone_number is intentionally omitted
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if success and 'order' in response:
            order = response['order']
            # Verify phone_number is empty string or None
            phone_empty = order.get('phone_number') in ['', None]
            self.test_data['order_without_phone'] = order
            return self.log_test("Create Order Without Phone", phone_empty, 
                               f"- Order created, phone_number: '{order.get('phone_number')}'")
        else:
            return self.log_test("Create Order Without Phone", False, 
                               f"- Status: {status}, Response: {response}")

    def test_create_order_with_phone(self):
        """Test creating order WITH phone number"""
        order_data = {
            "customer_name": "Lucia Bianchi",
            "delivery_address": "Via Roma 456, Milano, 20100 MI",
            "phone_number": "+39 333 1234567",
            "reference_number": "WITH-PHONE-001"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if success and 'order' in response:
            order = response['order']
            # Verify phone_number is stored correctly
            phone_correct = order.get('phone_number') == "+39 333 1234567"
            self.test_data['order_with_phone'] = order
            return self.log_test("Create Order With Phone", phone_correct, 
                               f"- Order created, phone_number: '{order.get('phone_number')}'")
        else:
            return self.log_test("Create Order With Phone", False, 
                               f"- Status: {status}, Response: {response}")

    def test_customer_creation_logic_without_phone(self):
        """Test customer creation logic when no phone number provided"""
        if 'order_without_phone' not in self.test_data:
            return self.log_test("Customer Creation Logic Without Phone", False, 
                               "- No order without phone available")
        
        order = self.test_data['order_without_phone']
        # When no phone is provided, customer_id should be None
        customer_id_none = order.get('customer_id') is None
        
        return self.log_test("Customer Creation Logic Without Phone", customer_id_none, 
                           f"- customer_id: {order.get('customer_id')} (should be None)")

    def test_customer_creation_logic_with_phone(self):
        """Test customer creation logic when phone number provided"""
        if 'order_with_phone' not in self.test_data:
            return self.log_test("Customer Creation Logic With Phone", False, 
                               "- No order with phone available")
        
        order = self.test_data['order_with_phone']
        # When phone is provided, customer should be auto-created
        customer_id_exists = order.get('customer_id') is not None
        
        if customer_id_exists:
            # Verify customer was actually created
            success, status, response = self.make_request(
                'GET', f'customers/{order["customer_id"]}',
                token=self.tokens['company_admin'],
                expected_status=200
            )
            
            if success and response.get('phone_number') == "+39 333 1234567":
                return self.log_test("Customer Creation Logic With Phone", True, 
                                   f"- Customer auto-created with ID: {order['customer_id']}")
            else:
                return self.log_test("Customer Creation Logic With Phone", False, 
                                   f"- Customer ID exists but customer not found or phone mismatch")
        else:
            return self.log_test("Customer Creation Logic With Phone", False, 
                               f"- customer_id: {order.get('customer_id')} (should not be None)")

    def test_assign_and_complete_order_without_phone(self):
        """Test order assignment and completion for order without phone"""
        if 'order_without_phone' not in self.test_data:
            return self.log_test("Assign and Complete Order Without Phone", False, 
                               "- No order without phone available")
        
        order_id = self.test_data['order_without_phone']['id']
        
        # Assign order to courier
        assign_data = {
            "order_id": order_id,
            "courier_id": self.test_data['courier_id']
        }
        
        success1, status1, response1 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Assign and Complete Order Without Phone", False, 
                               f"- Assignment failed: {status1}, {response1}")
        
        # Mark as delivered
        complete_data = {
            "order_id": order_id
        }
        
        success2, status2, response2 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=self.tokens['courier'],
            expected_status=200
        )
        
        if success2:
            return self.log_test("Assign and Complete Order Without Phone", True, 
                               "- Order assigned and completed successfully")
        else:
            return self.log_test("Assign and Complete Order Without Phone", False, 
                               f"- Completion failed: {status2}, {response2}")

    def test_assign_and_complete_order_with_phone(self):
        """Test order assignment and completion for order with phone"""
        if 'order_with_phone' not in self.test_data:
            return self.log_test("Assign and Complete Order With Phone", False, 
                               "- No order with phone available")
        
        order_id = self.test_data['order_with_phone']['id']
        
        # Assign order to courier
        assign_data = {
            "order_id": order_id,
            "courier_id": self.test_data['courier_id']
        }
        
        success1, status1, response1 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Assign and Complete Order With Phone", False, 
                               f"- Assignment failed: {status1}, {response1}")
        
        # Mark as delivered
        complete_data = {
            "order_id": order_id
        }
        
        success2, status2, response2 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=self.tokens['courier'],
            expected_status=200
        )
        
        if success2:
            return self.log_test("Assign and Complete Order With Phone", True, 
                               "- Order assigned and completed successfully")
        else:
            return self.log_test("Assign and Complete Order With Phone", False, 
                               f"- Completion failed: {status2}, {response2}")

    def test_sms_conditional_logic_no_phone(self):
        """Test that NO SMS is sent when order has no phone number"""
        if 'order_without_phone' not in self.test_data:
            return self.log_test("SMS Conditional Logic - No Phone", False, 
                               "- No order without phone available")
        
        # Wait a moment for SMS processing
        time.sleep(2)
        
        # Get SMS logs
        success, status, response = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success:
            return self.log_test("SMS Conditional Logic - No Phone", False, 
                               f"- Failed to get SMS logs: {status}")
        
        # Check if any SMS was sent for the order without phone
        order_id = self.test_data['order_without_phone']['id']
        sms_found = False
        
        for sms_log in response:
            # Check if SMS was sent for this customer (Giovanni Rossi)
            if 'Giovanni Rossi' in sms_log.get('message', ''):
                sms_found = True
                break
        
        # SMS should NOT be found for order without phone
        return self.log_test("SMS Conditional Logic - No Phone", not sms_found, 
                           f"- SMS correctly skipped for order without phone number")

    def test_sms_conditional_logic_with_phone(self):
        """Test that SMS IS sent when order has phone number"""
        if 'order_with_phone' not in self.test_data:
            return self.log_test("SMS Conditional Logic - With Phone", False, 
                               "- No order with phone available")
        
        # Wait a moment for SMS processing
        time.sleep(2)
        
        # Get SMS logs
        success, status, response = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success:
            return self.log_test("SMS Conditional Logic - With Phone", False, 
                               f"- Failed to get SMS logs: {status}")
        
        # Check if SMS was sent for the order with phone
        sms_found = False
        correct_phone = False
        italian_message = False
        
        for sms_log in response:
            # Check if SMS was sent for this customer (Lucia Bianchi) and phone
            if (sms_log.get('phone_number') == '+39 333 1234567' and 
                'Lucia Bianchi' in sms_log.get('message', '')):
                sms_found = True
                correct_phone = True
                if 'Ciao Lucia Bianchi!' in sms_log.get('message', '') and 'FarmyGo' in sms_log.get('message', ''):
                    italian_message = True
                break
        
        if sms_found and correct_phone and italian_message:
            return self.log_test("SMS Conditional Logic - With Phone", True, 
                               f"- SMS correctly sent to +39 333 1234567 with Italian message")
        elif sms_found and correct_phone:
            return self.log_test("SMS Conditional Logic - With Phone", False, 
                               f"- SMS sent but message format incorrect")
        elif sms_found:
            return self.log_test("SMS Conditional Logic - With Phone", False, 
                               f"- SMS found but phone number mismatch")
        else:
            return self.log_test("SMS Conditional Logic - With Phone", False, 
                               f"- No SMS found for order with phone number")

    def test_delivery_timestamp_accuracy(self):
        """Test that delivered_at timestamp is properly set and accurate"""
        # Get both orders to check their delivered_at timestamps
        orders_to_check = []
        
        if 'order_without_phone' in self.test_data:
            orders_to_check.append(('without_phone', self.test_data['order_without_phone']['id']))
        
        if 'order_with_phone' in self.test_data:
            orders_to_check.append(('with_phone', self.test_data['order_with_phone']['id']))
        
        if not orders_to_check:
            return self.log_test("Delivery Timestamp Accuracy", False, 
                               "- No completed orders available")
        
        all_timestamps_correct = True
        details = []
        
        for order_type, order_id in orders_to_check:
            # Get updated order data
            success, status, response = self.make_request(
                'GET', 'orders',
                token=self.tokens['company_admin'],
                expected_status=200
            )
            
            if not success:
                all_timestamps_correct = False
                details.append(f"{order_type}: Failed to get orders")
                continue
            
            # Find our order
            order_found = None
            for order in response:
                if order['id'] == order_id:
                    order_found = order
                    break
            
            if not order_found:
                all_timestamps_correct = False
                details.append(f"{order_type}: Order not found")
                continue
            
            # Check if delivered_at is set and order status is delivered
            if (order_found.get('status') == 'delivered' and 
                order_found.get('delivered_at') is not None):
                
                # Parse the timestamp to verify it's a valid datetime
                try:
                    delivered_at = order_found['delivered_at']
                    if isinstance(delivered_at, str):
                        # Try to parse ISO format datetime
                        datetime.fromisoformat(delivered_at.replace('Z', '+00:00'))
                    details.append(f"{order_type}: ✅ delivered_at set correctly")
                except:
                    all_timestamps_correct = False
                    details.append(f"{order_type}: ❌ delivered_at format invalid")
            else:
                all_timestamps_correct = False
                details.append(f"{order_type}: ❌ delivered_at not set or status not delivered")
        
        return self.log_test("Delivery Timestamp Accuracy", all_timestamps_correct, 
                           f"- {', '.join(details)}")

    def cleanup_test_environment(self):
        """Clean up test data"""
        print("🧹 Cleaning up test environment...")
        
        if 'company' in self.test_data:
            delete_data = {"password": "admin123"}
            success, status, response = self.make_request(
                'DELETE', f'companies/{self.test_data["company"]["id"]}',
                data=delete_data,
                token=self.tokens.get('super_admin'),
                expected_status=200
            )
            
            if success:
                print("✅ Test company deleted successfully")
            else:
                print(f"⚠️ Failed to delete test company: {status}")

    def run_optional_phone_tests(self):
        """Run all optional phone number tests"""
        print("🚀 Starting Optional Phone Number and SMS Conditional Logic Tests")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        # Test Scenarios
        print("\n📋 Test Scenario 1: Optional Phone Number in Order Creation")
        self.test_create_order_without_phone()
        self.test_create_order_with_phone()
        
        print("\n📋 Test Scenario 2: Customer Creation Logic")
        self.test_customer_creation_logic_without_phone()
        self.test_customer_creation_logic_with_phone()
        
        print("\n📋 Test Scenario 3: Order Assignment and Completion")
        self.test_assign_and_complete_order_without_phone()
        self.test_assign_and_complete_order_with_phone()
        
        print("\n📋 Test Scenario 4: SMS Conditional Logic")
        self.test_sms_conditional_logic_no_phone()
        self.test_sms_conditional_logic_with_phone()
        
        print("\n📋 Test Scenario 5: Delivery Timestamp Testing")
        self.test_delivery_timestamp_accuracy()
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All optional phone number tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the issues above.")
            return False

def main():
    tester = OptionalPhoneNumberTester()
    success = tester.run_optional_phone_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())