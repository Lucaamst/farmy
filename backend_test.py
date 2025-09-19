import requests
import sys
import json
from datetime import datetime
import urllib.parse

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
            
            # Try to parse JSON, but handle non-JSON responses
            try:
                response_data = response.json() if response.content else {}
            except:
                # For non-JSON responses (like file downloads), return content info
                response_data = {
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": len(response.content),
                    "is_binary": True
                }
            
            return success, response.status_code, response_data
        
        except Exception as e:
            return False, 0, {"error": str(e)}

    # ========== AUTHENTICATION TESTS ==========
    
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
            return self.log_test("Super Admin Login", True, f"- Token received, Role: {response['user']['role']}")
        else:
            return self.log_test("Super Admin Login", False, f"- Status: {status}, Response: {response}")

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "invalid", "password": "invalid"},
            expected_status=401
        )
        
        return self.log_test("Invalid Login", success, f"- Correctly rejected invalid credentials")

    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        # Test with invalid token
        success, status, response = self.make_request(
            'GET', 'companies',
            token="invalid_token",
            expected_status=401
        )
        
        return self.log_test("JWT Token Validation", success, f"- Invalid token correctly rejected")

    # ========== SUPER ADMIN API TESTS ==========
    
    def test_create_company(self):
        """Test creating a company with admin"""
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"FarmyGo_TestCompany_{timestamp}",
            "admin_username": f"farmygo_admin_{timestamp}",
            "admin_password": "SecurePass123!"
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

    def test_update_company(self):
        """Test updating company name"""
        if 'company' not in self.test_data:
            return self.log_test("Update Company", False, "- No company data available")
        
        company_id = self.test_data['company']['id']
        update_data = {
            "name": f"Updated_{self.test_data['company']['name']}"
        }
        
        success, status, response = self.make_request(
            'PATCH', f'companies/{company_id}',
            data=update_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        return self.log_test("Update Company", success, f"- Company name updated")

    def test_company_password_reset(self):
        """Test company admin password reset"""
        if 'company' not in self.test_data:
            return self.log_test("Company Password Reset", False, "- No company data available")
        
        company_id = self.test_data['company']['id']
        reset_data = {
            "company_id": company_id,
            "new_password": "NewSecurePass123!",
            "admin_password": "admin123"
        }
        
        success, status, response = self.make_request(
            'PATCH', f'companies/{company_id}/reset-password',
            data=reset_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if success:
            # Update stored credentials
            self.test_data['company_admin_creds']['password'] = "NewSecurePass123!"
        
        return self.log_test("Company Password Reset", success, f"- Password reset successfully")

    def test_toggle_company_status(self):
        """Test company enable/disable toggle"""
        if 'company' not in self.test_data:
            return self.log_test("Toggle Company Status", False, "- No company data available")
        
        company_id = self.test_data['company']['id']
        
        success, status, response = self.make_request(
            'PATCH', f'companies/{company_id}/toggle',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        return self.log_test("Toggle Company Status", success, f"- Company status toggled")

    # ========== COMPANY ADMIN AUTHENTICATION ==========
    
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
            return self.log_test("Company Admin Login", True, f"- Token received, Role: {response['user']['role']}")
        else:
            return self.log_test("Company Admin Login", False, f"- Status: {status}, Response: {response}")

    # ========== COURIER MANAGEMENT TESTS ==========
    
    def test_create_courier(self):
        """Test creating a courier"""
        timestamp = datetime.now().strftime('%H%M%S')
        courier_data = {
            "username": f"mario_rossi_{timestamp}",
            "password": "CourierPass123!"
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
                self.test_data['courier_data'] = response[0]
            return self.log_test("Get Couriers", True, f"- Found {len(response)} couriers")
        else:
            return self.log_test("Get Couriers", False, f"- Status: {status}, Response: {response}")

    def test_update_courier(self):
        """Test updating courier information"""
        if 'courier_id' not in self.test_data:
            return self.log_test("Update Courier", False, "- No courier data available")
        
        courier_id = self.test_data['courier_id']
        update_data = {
            "username": f"updated_{self.test_data['courier_creds']['username']}",
            "password": "UpdatedPass123!"
        }
        
        success, status, response = self.make_request(
            'PATCH', f'couriers/{courier_id}',
            data=update_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            # Update stored credentials
            self.test_data['courier_creds']['username'] = update_data['username']
            self.test_data['courier_creds']['password'] = update_data['password']
        
        return self.log_test("Update Courier", success, f"- Courier updated successfully")

    def test_toggle_courier_status(self):
        """Test courier block/unblock"""
        if 'courier_id' not in self.test_data:
            return self.log_test("Toggle Courier Status", False, "- No courier data available")
        
        courier_id = self.test_data['courier_id']
        
        # First toggle (should disable)
        success1, status1, response1 = self.make_request(
            'PATCH', f'couriers/{courier_id}/toggle',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Second toggle (should re-enable for later tests)
        success2, status2, response2 = self.make_request(
            'PATCH', f'couriers/{courier_id}/toggle',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        overall_success = success1 and success2
        return self.log_test("Toggle Courier Status", overall_success, f"- Courier status toggled twice (disable/enable)")

    # ========== CUSTOMER MANAGEMENT TESTS ==========
    
    def test_create_customer(self):
        """Test creating a customer"""
        customer_data = {
            "name": "Maria Bianchi",
            "phone_number": "+39 333 9876543",
            "address": "Via Garibaldi 45, Roma, 00185 RM",
            "email": "maria.bianchi@email.com",
            "notes": "Cliente VIP - consegne urgenti"
        }
        
        success, status, response = self.make_request(
            'POST', 'customers',
            data=customer_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'customer' in response:
            self.test_data['customer'] = response['customer']
            return self.log_test("Create Customer", True, f"- Customer: {response['customer']['name']}")
        else:
            return self.log_test("Create Customer", False, f"- Status: {status}, Response: {response}")

    def test_create_duplicate_customer_phone(self):
        """Test creating customer with duplicate phone number (should fail)"""
        if 'customer' not in self.test_data:
            return self.log_test("Create Duplicate Customer Phone", False, "- No customer data available")
        
        duplicate_data = {
            "name": "Different Name",
            "phone_number": self.test_data['customer']['phone_number'],
            "address": "Different Address",
            "email": "different@email.com"
        }
        
        success, status, response = self.make_request(
            'POST', 'customers',
            data=duplicate_data,
            token=self.tokens.get('company_admin'),
            expected_status=400
        )
        
        return self.log_test("Create Duplicate Customer Phone", success, f"- Duplicate phone correctly rejected")

    def test_get_customers(self):
        """Test getting customers list"""
        success, status, response = self.make_request(
            'GET', 'customers',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            return self.log_test("Get Customers", True, f"- Found {len(response)} customers")
        else:
            return self.log_test("Get Customers", False, f"- Status: {status}, Response: {response}")

    def test_get_specific_customer(self):
        """Test getting specific customer by ID"""
        if 'customer' not in self.test_data:
            return self.log_test("Get Specific Customer", False, "- No customer data available")
        
        customer_id = self.test_data['customer']['id']
        success, status, response = self.make_request(
            'GET', f'customers/{customer_id}',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'name' in response:
            return self.log_test("Get Specific Customer", True, f"- Customer: {response['name']}")
        else:
            return self.log_test("Get Specific Customer", False, f"- Status: {status}, Response: {response}")

    def test_update_customer(self):
        """Test updating customer information"""
        if 'customer' not in self.test_data:
            return self.log_test("Update Customer", False, "- No customer data available")
        
        customer_id = self.test_data['customer']['id']
        update_data = {
            "name": "Maria Bianchi Updated",
            "phone_number": "+39 333 9876544",  # Different phone
            "address": "Via Garibaldi 46, Roma, 00185 RM",
            "email": "maria.updated@email.com",
            "notes": "Cliente VIP - aggiornato"
        }
        
        success, status, response = self.make_request(
            'PATCH', f'customers/{customer_id}',
            data=update_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            # Update stored customer data
            self.test_data['customer']['phone_number'] = update_data['phone_number']
            self.test_data['customer']['name'] = update_data['name']
        
        return self.log_test("Update Customer", success, f"- Customer updated successfully")

    def test_search_customers(self):
        """Test customer search functionality"""
        if 'customer' not in self.test_data:
            return self.log_test("Search Customers", False, "- No customer data available")
        
        # Search by name
        success1, status1, response1 = self.make_request(
            'GET', 'customers/search',
            params={"query": "Maria"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Search by phone
        success2, status2, response2 = self.make_request(
            'GET', 'customers/search',
            params={"query": "333"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Search all customers (no query)
        success3, status3, response3 = self.make_request(
            'GET', 'customers/search',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        overall_success = success1 and success2 and success3
        return self.log_test("Search Customers", overall_success, f"- Customer search working correctly")

    def test_customer_order_history(self):
        """Test getting customer order history"""
        if 'customer' not in self.test_data:
            return self.log_test("Customer Order History", False, "- No customer data available")
        
        customer_id = self.test_data['customer']['id']
        success, status, response = self.make_request(
            'GET', f'customers/{customer_id}/orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            return self.log_test("Customer Order History", True, f"- Found {len(response)} orders for customer")
        else:
            return self.log_test("Customer Order History", False, f"- Status: {status}, Response: {response}")

    # ========== ORDER MANAGEMENT TESTS ==========
    
    def test_create_order(self):
        """Test creating a delivery order"""
        order_data = {
            "customer_name": "Giuseppe Verdi",
            "delivery_address": "Via Roma 123, Milano, 20121 MI",
            "phone_number": "+39 333 1234567",
            "reference_number": "ORD-2024-001"
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

    def test_update_order(self):
        """Test updating order information"""
        if 'order' not in self.test_data:
            return self.log_test("Update Order", False, "- No order data available")
        
        order_id = self.test_data['order']['id']
        update_data = {
            "customer_name": "Giuseppe Verdi Updated",
            "delivery_address": "Via Roma 456, Milano, 20121 MI",
            "phone_number": "+39 333 7654321",
            "reference_number": "ORD-2024-001-UPD"
        }
        
        success, status, response = self.make_request(
            'PATCH', f'orders/{order_id}',
            data=update_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        return self.log_test("Update Order", success, f"- Order updated successfully")

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

    def test_order_search_filters(self):
        """Test order search with various filters"""
        # Test search by customer name
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params={"customer_name": "Giuseppe"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test search by status
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            params={"status": "assigned"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test search by courier
        if 'courier_id' in self.test_data:
            success3, status3, response3 = self.make_request(
                'GET', 'orders/search',
                params={"courier_id": self.test_data['courier_id']},
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
        else:
            success3 = True
        
        overall_success = success1 and success2 and success3
        return self.log_test("Order Search Filters", overall_success, f"- Search filters working correctly")

    def test_order_export(self):
        """Test order export functionality"""
        # Test Excel export
        success1, status1, response1 = self.make_request(
            'GET', 'orders/export',
            params={"format": "excel"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test CSV export
        success2, status2, response2 = self.make_request(
            'GET', 'orders/export',
            params={"format": "csv"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        overall_success = success1 and success2
        if not overall_success:
            details = f"- Excel: {status1}, CSV: {status2}"
        else:
            details = f"- Export functionality working"
        return self.log_test("Order Export", overall_success, details)

    # ========== COURIER API TESTS ==========
    
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
            return self.log_test("Courier Login", True, f"- Token received, Role: {response['user']['role']}")
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
            return self.log_test("Mark Delivery Completed", True, "- SMS notification triggered")
        else:
            return self.log_test("Mark Delivery Completed", False, f"- Status: {status}, Response: {response}")

    # ========== SMS NOTIFICATION TESTS ==========
    
    def test_sms_logs(self):
        """Test SMS logs retrieval"""
        success, status, response = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            return self.log_test("SMS Logs", True, f"- Found {len(response)} SMS logs")
        else:
            return self.log_test("SMS Logs", False, f"- Status: {status}, Response: {response}")

    # ========== ROLE-BASED ACCESS CONTROL TESTS ==========
    
    def test_role_based_access_control(self):
        """Test role-based permissions"""
        # Test company admin trying to access super admin endpoint
        success1, status1, response1 = self.make_request(
            'GET', 'companies',
            token=self.tokens.get('company_admin'),
            expected_status=403
        )
        
        # Test courier trying to access company admin endpoint
        success2, status2, response2 = self.make_request(
            'GET', 'couriers',
            token=self.tokens.get('courier'),
            expected_status=403
        )
        
        overall_success = success1 and success2
        return self.log_test("Role-Based Access Control", overall_success, f"- Permissions correctly enforced")

    # ========== ERROR HANDLING TESTS ==========
    
    def test_error_handling(self):
        """Test various error scenarios"""
        # Test creating company with duplicate name
        if 'company' in self.test_data:
            success1, status1, response1 = self.make_request(
                'POST', 'companies',
                data={
                    "name": self.test_data['company']['name'],
                    "admin_username": "duplicate_test",
                    "admin_password": "test123"
                },
                token=self.tokens.get('super_admin'),
                expected_status=400
            )
        else:
            success1 = True
        
        # Test accessing non-existent order with valid UUID format
        success2, status2, response2 = self.make_request(
            'PATCH', 'orders/00000000-0000-0000-0000-000000000000',
            data={"customer_name": "Test", "delivery_address": "Test", "phone_number": "Test"},
            token=self.tokens.get('company_admin'),
            expected_status=404
        )
        
        overall_success = success1 and success2
        if not overall_success:
            details = f"- Duplicate company: {success1} ({status1}), Non-existent order: {success2} ({status2})"
        else:
            details = f"- Error scenarios handled correctly"
        return self.log_test("Error Handling", overall_success, details)

    # ========== CLEANUP TESTS ==========
    
    def test_delete_order(self):
        """Test deleting an order"""
        # Create a new order for deletion test
        order_data = {
            "customer_name": "Test Delete Order",
            "delivery_address": "Test Address",
            "phone_number": "+39 333 0000000"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success1 and 'order' in response1:
            order_id = response1['order']['id']
            success2, status2, response2 = self.make_request(
                'DELETE', f'orders/{order_id}',
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
            return self.log_test("Delete Order", success2, f"- Order deleted successfully")
        else:
            return self.log_test("Delete Order", False, f"- Could not create order for deletion test")

    def test_delete_courier(self):
        """Test deleting a courier"""
        # Create a new courier for deletion test
        timestamp = datetime.now().strftime('%H%M%S')
        courier_data = {
            "username": f"delete_test_{timestamp}",
            "password": "DeleteTest123!"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success1:
            # Get the courier ID
            success2, status2, response2 = self.make_request(
                'GET', 'couriers',
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
            
            if success2 and isinstance(response2, list):
                # Find the courier we just created
                courier_to_delete = None
                for courier in response2:
                    if courier['username'] == courier_data['username']:
                        courier_to_delete = courier
                        break
                
                if courier_to_delete:
                    success3, status3, response3 = self.make_request(
                        'DELETE', f'couriers/{courier_to_delete["id"]}',
                        token=self.tokens.get('company_admin'),
                        expected_status=200
                    )
                    return self.log_test("Delete Courier", success3, f"- Courier deleted successfully")
        
        return self.log_test("Delete Courier", False, f"- Could not complete courier deletion test")

    def test_delete_company(self):
        """Test deleting a company (cleanup)"""
        if 'company' not in self.test_data:
            return self.log_test("Delete Company", False, "- No company data available")
        
        company_id = self.test_data['company']['id']
        delete_data = {
            "password": "admin123"
        }
        
        success, status, response = self.make_request(
            'DELETE', f'companies/{company_id}',
            data=delete_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        return self.log_test("Delete Company", success, f"- Company deleted successfully")

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting FarmyGo Delivery Management API Comprehensive Tests")
        print("=" * 70)
        
        # Phase 1: Authentication Tests
        print("\n📋 Phase 1: Authentication & JWT Token Tests")
        self.test_super_admin_login()
        self.test_invalid_login()
        self.test_jwt_token_validation()
        
        # Phase 2: Super Admin API Tests
        print("\n📋 Phase 2: Super Admin API Tests")
        self.test_create_company()
        self.test_get_companies()
        self.test_update_company()
        self.test_company_password_reset()
        self.test_toggle_company_status()
        
        # Phase 3: Company Admin Authentication
        print("\n📋 Phase 3: Company Admin Authentication")
        self.test_company_admin_login()
        
        # Phase 4: Courier Management Tests
        print("\n📋 Phase 4: Courier Management Tests")
        self.test_create_courier()
        self.test_get_couriers()
        self.test_update_courier()
        self.test_toggle_courier_status()
        
        # Phase 5: Order Management Tests
        print("\n📋 Phase 5: Order Management Tests")
        self.test_create_order()
        self.test_get_orders()
        self.test_update_order()
        self.test_assign_order()
        self.test_order_search_filters()
        self.test_order_export()
        
        # Phase 6: Courier API Tests
        print("\n📋 Phase 6: Courier API Tests")
        self.test_courier_login()
        self.test_get_courier_deliveries()
        self.test_mark_delivery_completed()
        
        # Phase 7: SMS Notification Tests
        print("\n📋 Phase 7: SMS Notification Tests")
        self.test_sms_logs()
        
        # Phase 8: Security & Access Control Tests
        print("\n📋 Phase 8: Security & Access Control Tests")
        self.test_role_based_access_control()
        self.test_error_handling()
        
        # Phase 9: Cleanup Tests
        print("\n📋 Phase 9: Cleanup Tests")
        self.test_delete_order()
        self.test_delete_courier()
        self.test_delete_company()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! FarmyGo Backend API is working correctly.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the issues above.")
            return False

def main():
    tester = DeliveryManagementAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())