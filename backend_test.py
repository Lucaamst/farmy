import requests
import sys
import json
from datetime import datetime
import urllib.parse

class DeliveryManagementAPITester:
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
    
    def test_create_order_with_existing_customer(self):
        """Test creating order with existing customer ID"""
        if 'customer' not in self.test_data:
            return self.log_test("Create Order with Existing Customer", False, "- No customer data available")
        
        order_data = {
            "customer_name": "Giuseppe Verdi",
            "delivery_address": "Via Roma 123, Milano, 20121 MI",
            "phone_number": "+39 333 1234567",
            "reference_number": "ORD-2024-001",
            "customer_id": self.test_data['customer']['id']
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'order' in response:
            self.test_data['order'] = response['order']
            return self.log_test("Create Order with Existing Customer", True, f"- Order ID: {response['order']['id']}")
        else:
            return self.log_test("Create Order with Existing Customer", False, f"- Status: {status}, Response: {response}")

    def test_create_order_auto_customer_creation(self):
        """Test creating order with new phone number (auto customer creation)"""
        order_data = {
            "customer_name": "Antonio Rossi",
            "delivery_address": "Via Dante 789, Napoli, 80100 NA",
            "phone_number": "+39 333 5555555",  # New phone number
            "reference_number": "ORD-2024-002"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'order' in response:
            self.test_data['auto_created_order'] = response['order']
            # Verify customer was auto-created
            if response['order'].get('customer_id'):
                return self.log_test("Create Order Auto Customer Creation", True, f"- Order created with auto customer ID: {response['order']['customer_id']}")
            else:
                return self.log_test("Create Order Auto Customer Creation", False, f"- Order created but no customer_id found")
        else:
            return self.log_test("Create Order Auto Customer Creation", False, f"- Status: {status}, Response: {response}")

    def test_create_order_existing_phone_link(self):
        """Test creating order with existing phone number (should link to existing customer)"""
        if 'customer' not in self.test_data:
            return self.log_test("Create Order Existing Phone Link", False, "- No customer data available")
        
        order_data = {
            "customer_name": "Different Name",  # Different name but same phone
            "delivery_address": "Different Address",
            "phone_number": self.test_data['customer']['phone_number'],  # Existing phone
            "reference_number": "ORD-2024-003"
        }
        
        success, status, response = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and 'order' in response:
            # Verify it linked to existing customer
            if response['order'].get('customer_id') == self.test_data['customer']['id']:
                return self.log_test("Create Order Existing Phone Link", True, f"- Order linked to existing customer")
            else:
                return self.log_test("Create Order Existing Phone Link", False, f"- Order not linked to existing customer")
        else:
            return self.log_test("Create Order Existing Phone Link", False, f"- Status: {status}, Response: {response}")

    def test_create_order(self):
        """Test creating a basic delivery order"""
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
            if 'order' not in self.test_data:  # Only set if not already set by other tests
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

    # ========== SECURITY API TESTS ==========
    
    def test_security_status_api(self):
        """Test security status API for all user roles"""
        print("\n🔐 Testing Security Status API")
        
        # Test with super admin
        success1, status1, response1 = self.make_request(
            'GET', 'security/status',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        # Test with company admin
        success2, status2, response2 = self.make_request(
            'GET', 'security/status',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test with courier
        success3, status3, response3 = self.make_request(
            'GET', 'security/status',
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        # Test without authentication (should fail)
        success4, status4, response4 = self.make_request(
            'GET', 'security/status',
            expected_status=403  # HTTPBearer returns 403 when no auth header
        )
        
        # Verify response format
        format_correct = True
        if success1 and response1:
            required_fields = ['face_id_enabled', 'pin_enabled', 'sms_enabled', 'webauthn_credentials']
            format_correct = all(field in response1 for field in required_fields)
            # Check that values are boolean/int as expected
            defaults_correct = (
                isinstance(response1.get('face_id_enabled'), bool) and
                isinstance(response1.get('pin_enabled'), bool) and
                isinstance(response1.get('sms_enabled'), bool) and
                isinstance(response1.get('webauthn_credentials'), int)
            )
        else:
            format_correct = False
            defaults_correct = False
        
        overall_success = success1 and success2 and success3 and success4 and format_correct and defaults_correct
        
        if overall_success:
            return self.log_test("Security Status API", True, f"- All roles can access, proper format, correct types")
        else:
            details = f"- Super admin: {success1}, Company admin: {success2}, Courier: {success3}, No auth: {success4}, Format: {format_correct}, Types: {defaults_correct}"
            return self.log_test("Security Status API", False, details)

    def test_pin_security_system(self):
        """Test PIN security system setup and verification"""
        print("\n📱 Testing PIN Security System")
        
        # Test 1: Setup PIN with valid 6-digit PIN
        pin_data = {"pin": "123456"}
        success1, status1, response1 = self.make_request(
            'POST', 'security/setup-pin',
            data=pin_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: Setup PIN with invalid data (non-digits)
        invalid_pin_data = {"pin": "12345a"}
        success2, status2, response2 = self.make_request(
            'POST', 'security/setup-pin',
            data=invalid_pin_data,
            token=self.tokens.get('company_admin'),
            expected_status=400
        )
        
        # Test 3: Setup PIN with wrong length
        wrong_length_data = {"pin": "12345"}
        success3, status3, response3 = self.make_request(
            'POST', 'security/setup-pin',
            data=wrong_length_data,
            token=self.tokens.get('company_admin'),
            expected_status=400
        )
        
        # Test 4: Verify PIN with correct PIN
        verify_correct_data = {"pin": "123456"}
        success4, status4, response4 = self.make_request(
            'POST', 'security/verify-pin',
            data=verify_correct_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 5: Verify PIN with wrong PIN
        verify_wrong_data = {"pin": "654321"}
        success5, status5, response5 = self.make_request(
            'POST', 'security/verify-pin',
            data=verify_wrong_data,
            token=self.tokens.get('company_admin'),
            expected_status=401
        )
        
        # Test 6: Verify PIN without setup (using courier who hasn't set up PIN)
        success6, status6, response6 = self.make_request(
            'POST', 'security/verify-pin',
            data={"pin": "123456"},
            token=self.tokens.get('courier'),
            expected_status=400
        )
        
        # Test 7: Check security status after PIN setup
        success7, status7, response7 = self.make_request(
            'GET', 'security/status',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        pin_enabled = False
        if success7 and response7:
            pin_enabled = response7.get('pin_enabled') == True
        
        overall_success = success1 and success2 and success3 and success4 and success5 and success6 and success7 and pin_enabled
        
        if overall_success:
            return self.log_test("PIN Security System", True, f"- Setup, validation, verification all working correctly")
        else:
            details = f"- Setup: {success1}, Invalid chars: {success2}, Wrong length: {success3}, Verify correct: {success4}, Verify wrong: {success5}, No setup: {success6}, Status check: {success7}, PIN enabled: {pin_enabled}"
            return self.log_test("PIN Security System", False, details)

    def test_sms_security_system(self):
        """Test SMS security system"""
        print("\n📲 Testing SMS Security System")
        
        # Test 1: Send SMS code with valid Italian phone number (may fail due to Twilio permissions)
        sms_data = {"phone_number": "+39 333 1234567"}
        success1, status1, response1 = self.make_request(
            'POST', 'security/send-sms-code',
            data=sms_data,
            token=self.tokens.get('company_admin'),
            expected_status=[200, 500]  # 500 is expected if Twilio permissions not enabled
        )
        
        # Test 2: Verify SMS code with wrong code
        wrong_code_data = {
            "phone_number": "+39 333 1234567",
            "code": "000000"
        }
        success2, status2, response2 = self.make_request(
            'POST', 'security/verify-sms-code',
            data=wrong_code_data,
            token=self.tokens.get('company_admin'),
            expected_status=401
        )
        
        # Test 3: Verify SMS code with no code sent
        no_code_data = {
            "phone_number": "+39 333 9999999",
            "code": "123456"
        }
        success3, status3, response3 = self.make_request(
            'POST', 'security/verify-sms-code',
            data=no_code_data,
            token=self.tokens.get('company_admin'),
            expected_status=400
        )
        
        # Test 4: Check SMS logs were created
        success4, status4, response4 = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        sms_log_found = False
        if success4 and isinstance(response4, list):
            for log in response4:
                if log.get('phone_number') == '+39 333 1234567' and 'codice di verifica' in log.get('message', ''):
                    sms_log_found = True
                    break
        
        # Test 5: Test expired code scenario (we can't easily test this without waiting, so we'll simulate)
        # For now, we'll just test that the endpoint exists and responds correctly to basic scenarios
        
        # Check if SMS sending worked or failed due to expected Twilio permissions
        sms_send_worked = success1 or (status1 == 500)  # Either success or expected Twilio error
        
        overall_success = sms_send_worked and success2 and success3 and success4 and sms_log_found
        
        if overall_success:
            sms_status = "sent" if status1 == 200 else "failed (Twilio permissions)"
            return self.log_test("SMS Security System", True, f"- SMS {sms_status}, verification, and logging working correctly")
        else:
            details = f"- Send SMS: {sms_send_worked} ({status1}), Wrong code: {success2}, No code sent: {success3}, SMS logs: {success4}, Log found: {sms_log_found}"
            return self.log_test("SMS Security System", False, details)

    def test_webauthn_biometric_system(self):
        """Test WebAuthn/Biometric system"""
        print("\n👆 Testing WebAuthn/Biometric System")
        
        # Test 1: Generate registration options
        success1, status1, response1 = self.make_request(
            'POST', 'security/webauthn/generate-registration-options',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: Generate authentication options (should fail - no credentials registered)
        success2, status2, response2 = self.make_request(
            'POST', 'security/webauthn/generate-authentication-options',
            token=self.tokens.get('company_admin'),
            expected_status=400
        )
        
        # Test 3: Test error handling when WebAuthn is not available (if applicable)
        # This depends on whether webauthn library is installed
        webauthn_available = True
        if success1 and status1 == 501:  # Not implemented
            webauthn_available = False
        
        # For the purposes of this test, we'll consider it successful if:
        # - Registration options can be generated OR WebAuthn returns 501 (not available)
        # - Authentication options correctly fail when no credentials exist
        # - Error handling works properly
        
        if webauthn_available:
            # WebAuthn is available
            registration_works = success1
            auth_fails_correctly = success2  # Should fail with 400 when no credentials
            overall_success = registration_works and auth_fails_correctly
            
            if overall_success:
                return self.log_test("WebAuthn/Biometric System", True, f"- Registration options generated, authentication correctly requires credentials")
            else:
                details = f"- Registration: {success1} ({status1}), Auth without creds: {success2} ({status2})"
                return self.log_test("WebAuthn/Biometric System", False, details)
        else:
            # WebAuthn is not available (501 error)
            if status1 == 501:
                return self.log_test("WebAuthn/Biometric System", True, f"- WebAuthn not available (expected in some environments)")
            else:
                return self.log_test("WebAuthn/Biometric System", False, f"- Unexpected response when WebAuthn unavailable: {status1}")

    def test_security_authentication_requirements(self):
        """Test that all security endpoints require authentication"""
        print("\n🔒 Testing Security Authentication Requirements")
        
        # Test all security endpoints without authentication
        endpoints_to_test = [
            'security/status',
            'security/setup-pin',
            'security/verify-pin',
            'security/send-sms-code',
            'security/verify-sms-code',
            'security/webauthn/generate-registration-options',
            'security/webauthn/generate-authentication-options'
        ]
        
        all_protected = True
        failed_endpoints = []
        
        for endpoint in endpoints_to_test:
            if 'setup-pin' in endpoint or 'verify-pin' in endpoint or 'send-sms' in endpoint or 'verify-sms' in endpoint or 'webauthn' in endpoint:
                # POST endpoints
                success, status, response = self.make_request(
                    'POST', endpoint,
                    data={"test": "data"},
                    expected_status=403  # HTTPBearer returns 403 when no auth header
                )
            else:
                # GET endpoints
                success, status, response = self.make_request(
                    'GET', endpoint,
                    expected_status=403  # HTTPBearer returns 403 when no auth header
                )
            
            if not success:
                all_protected = False
                failed_endpoints.append(f"{endpoint}({status})")
        
        if all_protected:
            return self.log_test("Security Authentication Requirements", True, f"- All {len(endpoints_to_test)} security endpoints properly protected")
        else:
            return self.log_test("Security Authentication Requirements", False, f"- Failed endpoints: {', '.join(failed_endpoints)}")

    def test_security_different_user_roles(self):
        """Test security system with different user roles"""
        print("\n👥 Testing Security System with Different User Roles")
        
        # Test PIN setup for different roles
        roles_to_test = [
            ('super_admin', 'Super Admin'),
            ('company_admin', 'Company Admin'),
            ('courier', 'Courier')
        ]
        
        all_roles_work = True
        role_results = []
        
        for role_key, role_name in roles_to_test:
            if role_key not in self.tokens:
                continue
                
            # Setup PIN for this role (ensure exactly 6 digits)
            role_pin = f"{hash(role_key) % 1000000:06d}"  # Generate 6-digit PIN from role
            pin_data = {"pin": role_pin}
            success1, status1, response1 = self.make_request(
                'POST', 'security/setup-pin',
                data=pin_data,
                token=self.tokens.get(role_key),
                expected_status=200
            )
            
            # Verify PIN for this role
            success2, status2, response2 = self.make_request(
                'POST', 'security/verify-pin',
                data=pin_data,
                token=self.tokens.get(role_key),
                expected_status=200
            )
            
            # Check security status
            success3, status3, response3 = self.make_request(
                'GET', 'security/status',
                token=self.tokens.get(role_key),
                expected_status=200
            )
            
            role_success = success1 and success2 and success3
            role_results.append(f"{role_name}: {role_success}")
            
            if not role_success:
                all_roles_work = False
        
        if all_roles_work:
            return self.log_test("Security Different User Roles", True, f"- All user roles can use security features")
        else:
            return self.log_test("Security Different User Roles", False, f"- Role results: {', '.join(role_results)}")

    # ========== SMS NOTIFICATION TESTS ==========
    
    def test_twilio_sms_integration(self):
        """Test Twilio SMS integration specifically with Italian phone number"""
        print("\n🔔 Testing Twilio SMS Integration with Italian Phone Number")
        
        # Step 1: Create a test company and courier for SMS testing
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"SMS_Test_Company_{timestamp}",
            "admin_username": f"sms_admin_{timestamp}",
            "admin_password": "SMSTest123!"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Twilio SMS Integration - Create Company", False, f"- Status: {status1}, Response: {response1}")
        
        sms_company = response1['company']
        sms_admin_creds = {
            'username': company_data['admin_username'],
            'password': company_data['admin_password']
        }
        
        # Login as company admin
        success2, status2, response2 = self.make_request(
            'POST', 'auth/login',
            data={"username": sms_admin_creds['username'], "password": sms_admin_creds['password']},
            expected_status=200
        )
        
        if not success2:
            return self.log_test("Twilio SMS Integration - Admin Login", False, f"- Status: {status2}, Response: {response2}")
        
        sms_admin_token = response2['access_token']
        
        # Step 2: Create a courier for SMS testing
        courier_data = {
            "username": f"sms_courier_{timestamp}",
            "password": "SMSCourier123!"
        }
        
        success3, status3, response3 = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success3:
            return self.log_test("Twilio SMS Integration - Create Courier", False, f"- Status: {status3}, Response: {response3}")
        
        # Get courier ID
        success4, status4, response4 = self.make_request(
            'GET', 'couriers',
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success4 or not response4:
            return self.log_test("Twilio SMS Integration - Get Courier", False, f"- Status: {status4}")
        
        sms_courier_id = response4[0]['id']
        
        # Login as courier
        success5, status5, response5 = self.make_request(
            'POST', 'auth/login',
            data={"username": courier_data['username'], "password": courier_data['password']},
            expected_status=200
        )
        
        if not success5:
            return self.log_test("Twilio SMS Integration - Courier Login", False, f"- Status: {status5}, Response: {response5}")
        
        sms_courier_token = response5['access_token']
        
        # Step 3: Create a test order with Italian phone number
        order_data = {
            "customer_name": "Marco Bianchi",
            "delivery_address": "Via Nazionale 100, Roma, 00184 RM",
            "phone_number": "+39 333 1234567",  # Italian phone number format
            "reference_number": f"SMS-TEST-{timestamp}"
        }
        
        success6, status6, response6 = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success6:
            return self.log_test("Twilio SMS Integration - Create Order", False, f"- Status: {status6}, Response: {response6}")
        
        sms_order = response6['order']
        
        # Step 4: Assign order to courier
        assign_data = {
            "order_id": sms_order['id'],
            "courier_id": sms_courier_id
        }
        
        success7, status7, response7 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success7:
            return self.log_test("Twilio SMS Integration - Assign Order", False, f"- Status: {status7}, Response: {response7}")
        
        # Step 5: Mark order as delivered (this should trigger SMS)
        complete_data = {
            "order_id": sms_order['id']
        }
        
        success8, status8, response8 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_data,
            token=sms_courier_token,
            expected_status=200
        )
        
        if not success8:
            return self.log_test("Twilio SMS Integration - Mark Delivered", False, f"- Status: {status8}, Response: {response8}")
        
        # Step 6: Check SMS logs to verify SMS was sent
        import time
        time.sleep(2)  # Wait for SMS to be processed
        
        success9, status9, response9 = self.make_request(
            'GET', 'sms-logs',
            token=sms_admin_token,
            expected_status=200
        )
        
        if not success9:
            return self.log_test("Twilio SMS Integration - Get SMS Logs", False, f"- Status: {status9}, Response: {response9}")
        
        # Verify SMS log contains our test
        sms_found = False
        twilio_used = False
        italian_message = False
        
        for sms_log in response9:
            if sms_log.get('phone_number') == "+39 333 1234567":
                sms_found = True
                if sms_log.get('method') == 'twilio':
                    twilio_used = True
                if 'Ciao Marco Bianchi!' in sms_log.get('message', '') and 'FarmyGo' in sms_log.get('message', ''):
                    italian_message = True
                break
        
        # Step 7: Cleanup - Delete test company
        delete_data = {"password": "admin123"}
        self.make_request(
            'DELETE', f'companies/{sms_company["id"]}',
            data=delete_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        # Evaluate results
        if sms_found and twilio_used and italian_message:
            return self.log_test("Twilio SMS Integration", True, f"- SMS sent via Twilio with Italian message to +39 333 1234567")
        elif sms_found and not twilio_used:
            return self.log_test("Twilio SMS Integration", False, f"- SMS found but used mock instead of Twilio")
        elif sms_found and not italian_message:
            return self.log_test("Twilio SMS Integration", False, f"- SMS sent but message format incorrect")
        else:
            return self.log_test("Twilio SMS Integration", False, f"- No SMS log found for test phone number")
    
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

    def test_delete_customer_with_orders(self):
        """Test deleting customer with orders (should fail)"""
        if 'customer' not in self.test_data:
            return self.log_test("Delete Customer with Orders", False, "- No customer data available")
        
        customer_id = self.test_data['customer']['id']
        success, status, response = self.make_request(
            'DELETE', f'customers/{customer_id}',
            token=self.tokens.get('company_admin'),
            expected_status=400
        )
        
        return self.log_test("Delete Customer with Orders", success, f"- Customer deletion correctly blocked due to existing orders")

    def test_delete_customer_without_orders(self):
        """Test deleting customer without orders"""
        # Create a new customer for deletion test
        customer_data = {
            "name": "Test Delete Customer",
            "phone_number": "+39 333 0000001",
            "address": "Test Address for Deletion"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'customers',
            data=customer_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success1 and 'customer' in response1:
            customer_id = response1['customer']['id']
            success2, status2, response2 = self.make_request(
                'DELETE', f'customers/{customer_id}',
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
            return self.log_test("Delete Customer without Orders", success2, f"- Customer deleted successfully")
        else:
            return self.log_test("Delete Customer without Orders", False, f"- Could not create customer for deletion test")

    # ========== SMS STATISTICS API TESTS ==========
    
    def test_sms_statistics_api_access(self):
        """Test SMS statistics API access and authentication"""
        print("\n📊 Testing SMS Statistics API Access")
        
        # Test 1: Super Admin can access SMS stats
        success1, status1, response1 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        # Test 2: Company Admin cannot access SMS stats (should be forbidden)
        success2, status2, response2 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('company_admin'),
            expected_status=403
        )
        
        # Test 3: Courier cannot access SMS stats (should be forbidden)
        success3, status3, response3 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('courier'),
            expected_status=403
        )
        
        # Test 4: No authentication (should be forbidden)
        success4, status4, response4 = self.make_request(
            'GET', 'super-admin/sms-stats',
            expected_status=403
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
        
        overall_success = success1 and success2 and success3 and success4 and format_correct
        
        if overall_success:
            return self.log_test("SMS Statistics API Access", True, f"- Super Admin access ✅, Others blocked ✅, Format correct ✅")
        else:
            details = f"- Super Admin: {success1}, Company Admin blocked: {success2}, Courier blocked: {success3}, No auth blocked: {success4}, Format: {format_correct}"
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
        
        # Test 5: Company Admin cannot update cost settings
        success5, status5, response5 = self.make_request(
            'PUT', 'super-admin/sms-cost-settings',
            data=new_cost_data,
            token=self.tokens.get('company_admin'),
            expected_status=403
        )
        
        # Test 6: Restore original cost settings
        restore_data = {
            "cost_per_sms": initial_cost,
            "currency": "EUR"
        }
        
        success6, status6, response6 = self.make_request(
            'PUT', 'super-admin/sms-cost-settings',
            data=restore_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        overall_success = success1 and success2 and success3 and settings_updated and success4 and success5 and success6
        
        if overall_success:
            return self.log_test("SMS Cost Settings API", True, f"- Update ✅, Validation ✅, Access control ✅, Restore ✅")
        else:
            details = f"- Get initial: {success1}, Update: {success2}, Verify: {success3}, Updated: {settings_updated}, Negative rejected: {success4}, Access blocked: {success5}, Restore: {success6}"
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
        
        # Test 3: Company Admin cannot access monthly report
        success3, status3, response3 = self.make_request(
            'GET', 'super-admin/sms-monthly-report',
            params={"year": current_year, "month": current_month},
            token=self.tokens.get('company_admin'),
            expected_status=403
        )
        
        # Test 4: Test with invalid parameters (missing year/month)
        success4, status4, response4 = self.make_request(
            'GET', 'super-admin/sms-monthly-report',
            token=self.tokens.get('super_admin'),
            expected_status=422  # FastAPI validation error
        )
        
        # Verify response format if data exists
        format_correct = True
        if success1 and status1 == 200 and response1:
            required_fields = ['monthly_stats', 'daily_breakdown', 'period']
            format_correct = all(field in response1 for field in required_fields)
        
        overall_success = success1 and success2 and success3 and success4 and format_correct
        
        if overall_success:
            data_status = "with data" if status1 == 200 else "no data (expected)"
            return self.log_test("SMS Monthly Report API", True, f"- Current month {data_status} ✅, Non-existent month 404 ✅, Access control ✅, Validation ✅")
        else:
            details = f"- Current month: {success1} ({status1}), Non-existent: {success2}, Access blocked: {success3}, Validation: {success4}, Format: {format_correct}"
            return self.log_test("SMS Monthly Report API", False, details)

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
        import time
        time.sleep(2)
        
        # Step 7: Check if SMS statistics were updated
        success10, status10, response10 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        sms_count_increased = False
        company_tracked = False
        if success10 and response10 and 'year_to_date' in response10:
            new_sms_count = response10['year_to_date'].get('total_sms', 0)
            sms_count_increased = new_sms_count > initial_sms_count
            
            # Check if company is tracked in breakdown
            if 'companies_breakdown' in response10:
                company_tracked = track_company['id'] in response10['companies_breakdown']
        
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

    def test_sms_tracking_success_vs_failed(self):
        """Test SMS tracking for both successful and failed SMS attempts"""
        print("\n📈 Testing SMS Tracking for Success vs Failed SMS")
        
        # Get initial statistics
        success1, status1, response1 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        initial_total = 0
        initial_successful = 0
        initial_failed = 0
        
        if success1 and response1 and 'year_to_date' in response1:
            initial_total = response1['year_to_date'].get('total_sms', 0)
            # We need to calculate success/failed from current month or monthly history
            if 'current_month' in response1 and response1['current_month']:
                initial_successful = response1['current_month'].get('successful_sms', 0)
                initial_failed = response1['current_month'].get('failed_sms', 0)
        
        # Test SMS sending through security system (this will likely fail due to Twilio permissions)
        # This failure will be tracked in statistics
        sms_data = {"phone_number": "+39 333 8888888"}
        success2, status2, response2 = self.make_request(
            'POST', 'security/send-sms-code',
            data=sms_data,
            token=self.tokens.get('super_admin'),
            expected_status=[200, 500]  # 500 expected if Twilio permissions not enabled
        )
        
        # Wait for SMS processing
        import time
        time.sleep(2)
        
        # Check updated statistics
        success3, status3, response3 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        stats_updated = False
        sms_tracked_correctly = False
        
        if success3 and response3:
            new_total = response3['year_to_date'].get('total_sms', 0)
            stats_updated = new_total > initial_total
            
            # Check current month stats for success/failed breakdown
            if 'current_month' in response3 and response3['current_month']:
                new_successful = response3['current_month'].get('successful_sms', 0)
                new_failed = response3['current_month'].get('failed_sms', 0)
                
                if status2 == 200:
                    # SMS should have been successful
                    sms_tracked_correctly = new_successful > initial_successful
                else:
                    # SMS should have failed
                    sms_tracked_correctly = new_failed > initial_failed
        
        # Check SMS logs to verify tracking
        success4, status4, response4 = self.make_request(
            'GET', 'sms-logs',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        sms_log_found = False
        log_status_correct = False
        
        if success4 and isinstance(response4, list):
            for log in response4:
                if log.get('phone_number') == "+39 333 8888888":
                    sms_log_found = True
                    log_status = log.get('status')
                    if status2 == 200:
                        log_status_correct = log_status == 'sent'
                    else:
                        log_status_correct = log_status == 'failed'
                    break
        
        overall_success = stats_updated and sms_tracked_correctly and sms_log_found and log_status_correct
        
        if overall_success:
            sms_result = "successful" if status2 == 200 else "failed (expected)"
            return self.log_test("SMS Tracking Success vs Failed", True, 
                               f"- SMS {sms_result} ✅, Statistics updated ✅, Tracking correct ✅, Log status correct ✅")
        else:
            details = f"- Stats updated: {stats_updated}, SMS tracked correctly: {sms_tracked_correctly}, Log found: {sms_log_found}, Log status correct: {log_status_correct}"
            return self.log_test("SMS Tracking Success vs Failed", False, details)

    def test_sms_statistics_company_breakdown(self):
        """Test that SMS statistics correctly track company_id breakdown"""
        print("\n🏢 Testing SMS Statistics Company Breakdown")
        
        # Create a test company for company-specific SMS tracking
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"SMS_Breakdown_Company_{timestamp}",
            "admin_username": f"sms_breakdown_admin_{timestamp}",
            "admin_password": "SMSBreakdown123!"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("SMS Statistics Company Breakdown - Create Company", False, f"- Status: {status1}")
        
        breakdown_company = response1['company']
        breakdown_admin_creds = {
            'username': company_data['admin_username'],
            'password': company_data['admin_password']
        }
        
        # Login as company admin
        success2, status2, response2 = self.make_request(
            'POST', 'auth/login',
            data={"username": breakdown_admin_creds['username'], "password": breakdown_admin_creds['password']},
            expected_status=200
        )
        
        if not success2:
            return self.log_test("SMS Statistics Company Breakdown - Admin Login", False, f"- Status: {status2}")
        
        breakdown_admin_token = response2['access_token']
        
        # Get initial company breakdown
        success3, status3, response3 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        initial_company_stats = {}
        if success3 and response3 and 'companies_breakdown' in response3:
            initial_company_stats = response3['companies_breakdown'].get(breakdown_company['id'], {})
        
        # Send SMS from this company (through security system)
        sms_data = {"phone_number": "+39 333 9999999"}
        success4, status4, response4 = self.make_request(
            'POST', 'security/send-sms-code',
            data=sms_data,
            token=breakdown_admin_token,
            expected_status=[200, 500]  # 500 expected if Twilio permissions not enabled
        )
        
        # Wait for SMS processing
        import time
        time.sleep(2)
        
        # Check updated company breakdown
        success5, status5, response5 = self.make_request(
            'GET', 'super-admin/sms-stats',
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        company_tracked = False
        company_stats_updated = False
        
        if success5 and response5 and 'companies_breakdown' in response5:
            company_breakdown = response5['companies_breakdown']
            
            if breakdown_company['id'] in company_breakdown:
                company_tracked = True
                company_stats = company_breakdown[breakdown_company['id']]
                
                # Check if company name is included
                if 'name' in company_stats and company_stats['name'] == breakdown_company['name']:
                    # Check if stats were updated
                    if 'stats' in company_stats:
                        stats = company_stats['stats']
                        initial_sent = initial_company_stats.get('stats', {}).get('sent', 0) if initial_company_stats else 0
                        new_sent = stats.get('sent', 0)
                        company_stats_updated = new_sent > initial_sent
        
        # Verify SMS log has correct company_id
        success6, status6, response6 = self.make_request(
            'GET', 'sms-logs',
            token=breakdown_admin_token,
            expected_status=200
        )
        
        company_id_in_log = False
        if success6 and isinstance(response6, list):
            for log in response6:
                if (log.get('phone_number') == "+39 333 9999999" and 
                    log.get('company_id') == breakdown_company['id']):
                    company_id_in_log = True
                    break
        
        # Cleanup - Delete test company
        delete_data = {"password": "admin123"}
        self.make_request(
            'DELETE', f'companies/{breakdown_company["id"]}',
            data=delete_data,
            token=self.tokens.get('super_admin'),
            expected_status=200
        )
        
        overall_success = company_tracked and company_stats_updated and company_id_in_log
        
        if overall_success:
            return self.log_test("SMS Statistics Company Breakdown", True, 
                               f"- Company tracked ✅, Stats updated ✅, Company ID in logs ✅")
        else:
            details = f"- Company tracked: {company_tracked}, Stats updated: {company_stats_updated}, Company ID in log: {company_id_in_log}"
            return self.log_test("SMS Statistics Company Breakdown", False, details)

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

    # ========== FARMYGO ORDER VISIBILITY & FILTERING TESTS ==========
    
    def test_order_creation_immediate_visibility(self):
        """Test that newly created orders appear immediately in orders list"""
        print("\n📦 Testing Order Creation and Immediate Visibility")
        
        # Get initial order count
        success1, status1, response1 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Order Creation Immediate Visibility - Get Initial Orders", False, f"- Status: {status1}")
        
        initial_count = len(response1) if isinstance(response1, list) else 0
        
        # Create a new order
        timestamp = datetime.now().strftime('%H%M%S')
        order_data = {
            "customer_name": f"Visibility Test Customer {timestamp}",
            "delivery_address": "Via Test Visibility 123, Roma, 00100 RM",
            "phone_number": f"+39 333 {timestamp}",
            "reference_number": f"VIS-TEST-{timestamp}"
        }
        
        success2, status2, response2 = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success2:
            return self.log_test("Order Creation Immediate Visibility - Create Order", False, f"- Status: {status2}, Response: {response2}")
        
        created_order = response2['order']
        
        # Immediately check if order appears in orders list
        success3, status3, response3 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success3:
            return self.log_test("Order Creation Immediate Visibility - Get Orders After Creation", False, f"- Status: {status3}")
        
        new_count = len(response3) if isinstance(response3, list) else 0
        order_found = any(order['id'] == created_order['id'] for order in response3)
        
        # Store created order for later tests
        self.test_data['visibility_test_order'] = created_order
        
        if new_count == initial_count + 1 and order_found:
            return self.log_test("Order Creation Immediate Visibility", True, f"- Order appears immediately (count: {initial_count} → {new_count})")
        else:
            return self.log_test("Order Creation Immediate Visibility", False, f"- Order not visible immediately (count: {initial_count} → {new_count}, found: {order_found})")

    def test_order_creation_with_without_phone(self):
        """Test creating orders with and without phone numbers"""
        print("\n📱 Testing Order Creation With/Without Phone Numbers")
        
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Test 1: Create order WITH phone number
        order_with_phone = {
            "customer_name": f"Customer With Phone {timestamp}",
            "delivery_address": "Via Phone Test 456, Milano, 20100 MI",
            "phone_number": f"+39 333 {timestamp}1",
            "reference_number": f"PHONE-{timestamp}"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=order_with_phone,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: Create order WITHOUT phone number (optional field)
        order_without_phone = {
            "customer_name": f"Customer No Phone {timestamp}",
            "delivery_address": "Via No Phone Test 789, Napoli, 80100 NA",
            "reference_number": f"NOPHONE-{timestamp}"
            # phone_number is intentionally omitted
        }
        
        success2, status2, response2 = self.make_request(
            'POST', 'orders',
            data=order_without_phone,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 3: Verify both orders appear in orders list
        success3, status3, response3 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success3 and isinstance(response3, list):
            phone_order_found = any(order.get('reference_number') == f"PHONE-{timestamp}" for order in response3)
            no_phone_order_found = any(order.get('reference_number') == f"NOPHONE-{timestamp}" for order in response3)
        else:
            phone_order_found = False
            no_phone_order_found = False
        
        overall_success = success1 and success2 and success3 and phone_order_found and no_phone_order_found
        
        if overall_success:
            return self.log_test("Order Creation With/Without Phone", True, f"- Both order types created and visible")
        else:
            details = f"- With phone: {success1}, Without phone: {success2}, List: {success3}, Found with phone: {phone_order_found}, Found without phone: {no_phone_order_found}"
            return self.log_test("Order Creation With/Without Phone", False, details)

    def test_order_filtering_empty_null_filters(self):
        """Test that empty/null filters don't cause errors"""
        print("\n🔍 Testing Order Filtering with Empty/Null Filters")
        
        # Test 1: Empty string filters
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params={
                "customer_name": "",
                "courier_id": "",
                "status": "",
                "date_from": "",
                "date_to": ""
            },
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: None/null filters (omitted parameters)
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 3: Mixed empty and valid filters
        success3, status3, response3 = self.make_request(
            'GET', 'orders/search',
            params={
                "customer_name": "",
                "status": "pending"
            },
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        overall_success = success1 and success2 and success3
        
        if overall_success:
            return self.log_test("Order Filtering Empty/Null Filters", True, f"- Empty filters handled correctly")
        else:
            details = f"- Empty strings: {success1} ({status1}), No params: {success2} ({status2}), Mixed: {success3} ({status3})"
            return self.log_test("Order Filtering Empty/Null Filters", False, details)

    def test_order_filtering_individual_filters(self):
        """Test individual order filters"""
        print("\n🎯 Testing Individual Order Filters")
        
        # Ensure we have test data
        if 'visibility_test_order' not in self.test_data:
            return self.log_test("Individual Order Filters", False, "- No test order available")
        
        test_order = self.test_data['visibility_test_order']
        
        # Test 1: Filter by customer name
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params={"customer_name": "Visibility Test"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: Filter by status
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            params={"status": "pending"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 3: Filter by date (today)
        today = datetime.now().strftime('%Y-%m-%d')
        success3, status3, response3 = self.make_request(
            'GET', 'orders/search',
            params={"date_from": today},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Verify results contain expected data
        name_filter_works = success1 and isinstance(response1, list) and any(
            'Visibility Test' in order.get('customer_name', '') for order in response1
        )
        
        status_filter_works = success2 and isinstance(response2, list) and all(
            order.get('status') == 'pending' for order in response2 if response2
        )
        
        date_filter_works = success3 and isinstance(response3, list)
        
        overall_success = name_filter_works and status_filter_works and date_filter_works
        
        if overall_success:
            return self.log_test("Individual Order Filters", True, f"- Name, status, and date filters working")
        else:
            details = f"- Name filter: {name_filter_works}, Status filter: {status_filter_works}, Date filter: {date_filter_works}"
            return self.log_test("Individual Order Filters", False, details)

    def test_order_filtering_combinations(self):
        """Test combination of multiple filters"""
        print("\n🔗 Testing Multiple Filter Combinations")
        
        # Test 1: Customer name + status
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params={
                "customer_name": "Test",
                "status": "pending"
            },
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: Status + date range
        today = datetime.now().strftime('%Y-%m-%d')
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            params={
                "status": "pending",
                "date_from": today
            },
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 3: All filters combined
        if 'courier_id' in self.test_data:
            success3, status3, response3 = self.make_request(
                'GET', 'orders/search',
                params={
                    "customer_name": "Test",
                    "courier_id": self.test_data['courier_id'],
                    "status": "assigned",
                    "date_from": today
                },
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
        else:
            success3 = True  # Skip if no courier available
        
        overall_success = success1 and success2 and success3
        
        if overall_success:
            return self.log_test("Multiple Filter Combinations", True, f"- Filter combinations working correctly")
        else:
            details = f"- Name+Status: {success1} ({status1}), Status+Date: {success2} ({status2}), All filters: {success3}"
            return self.log_test("Multiple Filter Combinations", False, details)

    def test_order_filtering_clear_filters(self):
        """Test that clearing filters returns to showing all orders"""
        print("\n🧹 Testing Filter Clearing Behavior")
        
        # Get all orders (no filters)
        success1, status1, response1 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Get orders with search but no filters (should be same as above)
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Apply a filter
        success3, status3, response3 = self.make_request(
            'GET', 'orders/search',
            params={"status": "pending"},
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Clear filters (back to no parameters)
        success4, status4, response4 = self.make_request(
            'GET', 'orders/search',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success1 and success2 and success4:
            all_orders_count = len(response1) if isinstance(response1, list) else 0
            search_no_filter_count = len(response2) if isinstance(response2, list) else 0
            cleared_filter_count = len(response4) if isinstance(response4, list) else 0
            
            # All three should return the same number of orders
            counts_match = all_orders_count == search_no_filter_count == cleared_filter_count
            
            if counts_match:
                return self.log_test("Filter Clearing Behavior", True, f"- Clearing filters returns all {all_orders_count} orders")
            else:
                return self.log_test("Filter Clearing Behavior", False, f"- Count mismatch: all={all_orders_count}, search={search_no_filter_count}, cleared={cleared_filter_count}")
        else:
            details = f"- Get all: {success1}, Search no filter: {success2}, Filtered: {success3}, Cleared: {success4}"
            return self.log_test("Filter Clearing Behavior", False, details)

    def test_courier_full_name_assignment(self):
        """Test order assignment with couriers having full names"""
        print("\n👤 Testing Courier Full Name Assignment")
        
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Create courier with full name
        courier_data = {
            "username": f"fullname_courier_{timestamp}",
            "password": "FullNameTest123!",
            "full_name": "Mario Rossi Delivery Expert"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Courier Full Name Assignment - Create Courier", False, f"- Status: {status1}")
        
        # Get courier list to find the ID
        success2, status2, response2 = self.make_request(
            'GET', 'couriers',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success2:
            return self.log_test("Courier Full Name Assignment - Get Couriers", False, f"- Status: {status2}")
        
        # Find our courier
        test_courier = None
        for courier in response2:
            if courier.get('username') == courier_data['username']:
                test_courier = courier
                break
        
        if not test_courier:
            return self.log_test("Courier Full Name Assignment - Find Courier", False, "- Courier not found in list")
        
        # Verify full_name field is present
        if 'full_name' not in test_courier or test_courier['full_name'] != courier_data['full_name']:
            return self.log_test("Courier Full Name Assignment - Full Name Field", False, f"- Full name not stored correctly")
        
        # Create an order for assignment
        order_data = {
            "customer_name": f"Assignment Test Customer {timestamp}",
            "delivery_address": "Via Assignment Test 999, Roma, 00100 RM",
            "phone_number": f"+39 333 {timestamp}9",
            "reference_number": f"ASSIGN-{timestamp}"
        }
        
        success3, status3, response3 = self.make_request(
            'POST', 'orders',
            data=order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success3:
            return self.log_test("Courier Full Name Assignment - Create Order", False, f"- Status: {status3}")
        
        test_order = response3['order']
        
        # Assign order to courier with full name
        assign_data = {
            "order_id": test_order['id'],
            "courier_id": test_courier['id']
        }
        
        success4, status4, response4 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success4:
            return self.log_test("Courier Full Name Assignment - Assign Order", False, f"- Status: {status4}, Response: {response4}")
        
        # Verify assignment worked
        success5, status5, response5 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success5:
            assigned_order = None
            for order in response5:
                if order['id'] == test_order['id']:
                    assigned_order = order
                    break
            
            if assigned_order and assigned_order.get('courier_id') == test_courier['id'] and assigned_order.get('status') == 'assigned':
                return self.log_test("Courier Full Name Assignment", True, f"- Order assigned to courier with full name: {courier_data['full_name']}")
            else:
                return self.log_test("Courier Full Name Assignment", False, f"- Assignment not reflected in order")
        else:
            return self.log_test("Courier Full Name Assignment", False, f"- Could not verify assignment")

    def test_orders_default_behavior_no_date_filter(self):
        """Test that GET /api/orders returns all orders without date filtering"""
        print("\n📅 Testing Orders Default Behavior (No Date Filter)")
        
        # Create orders on different dates (simulate by creating multiple orders)
        timestamp = datetime.now().strftime('%H%M%S')
        orders_created = []
        
        for i in range(3):
            order_data = {
                "customer_name": f"Default Behavior Test {timestamp}_{i}",
                "delivery_address": f"Via Default Test {i}, Roma, 0010{i} RM",
                "phone_number": f"+39 333 {timestamp}{i}",
                "reference_number": f"DEFAULT-{timestamp}-{i}"
            }
            
            success, status, response = self.make_request(
                'POST', 'orders',
                data=order_data,
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
            
            if success and 'order' in response:
                orders_created.append(response['order'])
        
        if len(orders_created) != 3:
            return self.log_test("Orders Default Behavior - Create Test Orders", False, f"- Only created {len(orders_created)}/3 orders")
        
        # Test 1: GET /api/orders (should return all orders)
        success1, status1, response1 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: GET /api/orders/search with no date filters (should return all orders)
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 3: Verify our test orders are in both responses
        if success1 and success2:
            all_orders_ids = [order['id'] for order in response1] if isinstance(response1, list) else []
            search_orders_ids = [order['id'] for order in response2] if isinstance(response2, list) else []
            
            test_orders_in_all = all(order['id'] in all_orders_ids for order in orders_created)
            test_orders_in_search = all(order['id'] in search_orders_ids for order in orders_created)
            
            # Both endpoints should return the same orders
            same_results = set(all_orders_ids) == set(search_orders_ids)
            
            if test_orders_in_all and test_orders_in_search and same_results:
                return self.log_test("Orders Default Behavior (No Date Filter)", True, f"- All orders returned without date filtering ({len(response1)} orders)")
            else:
                details = f"- Test orders in /orders: {test_orders_in_all}, in /search: {test_orders_in_search}, same results: {same_results}"
                return self.log_test("Orders Default Behavior (No Date Filter)", False, details)
        else:
            details = f"- GET /orders: {success1} ({status1}), GET /orders/search: {success2} ({status2})"
            return self.log_test("Orders Default Behavior (No Date Filter)", False, details)

    def run_farmygo_order_visibility_tests(self):
        """Run focused tests for FarmyGo order visibility and filtering issues"""
        print("🎯 Starting FarmyGo Order Visibility & Filtering Tests")
        print("=" * 70)
        
        # Ensure we have authentication
        if not self.tokens.get('company_admin'):
            print("❌ No company admin token available. Running basic authentication first...")
            self.test_super_admin_login()
            self.test_create_company()
            self.test_company_admin_login()
        
        # Run focused tests
        print("\n📋 FarmyGo Order Visibility & Filtering Tests")
        self.test_order_creation_immediate_visibility()
        self.test_order_creation_with_without_phone()
        self.test_order_filtering_empty_null_filters()
        self.test_order_filtering_individual_filters()
        self.test_order_filtering_combinations()
        self.test_order_filtering_clear_filters()
        self.test_courier_full_name_assignment()
        self.test_orders_default_behavior_no_date_filter()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 FarmyGo Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All FarmyGo order visibility and filtering tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            return False

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
        
        # Phase 5: Customer Management Tests
        print("\n📋 Phase 5: Customer Management Tests")
        self.test_create_customer()
        self.test_create_duplicate_customer_phone()
        self.test_get_customers()
        self.test_get_specific_customer()
        self.test_update_customer()
        self.test_search_customers()
        self.test_customer_order_history()
        
        # Phase 6: Order Management Tests (with Customer Integration)
        print("\n📋 Phase 6: Order Management Tests (with Customer Integration)")
        self.test_create_order_with_existing_customer()
        self.test_create_order_auto_customer_creation()
        self.test_create_order_existing_phone_link()
        self.test_create_order()
        self.test_get_orders()
        self.test_update_order()
        self.test_assign_order()
        self.test_order_search_filters()
        self.test_order_export()
        
        # Phase 7: Courier API Tests
        print("\n📋 Phase 7: Courier API Tests")
        self.test_courier_login()
        self.test_get_courier_deliveries()
        self.test_mark_delivery_completed()
        
        # Phase 8: SMS Notification Tests
        print("\n📋 Phase 8: SMS Notification Tests")
        self.test_twilio_sms_integration()
        self.test_sms_logs()
        
        # Phase 9: Multi-Level Security System Tests
        print("\n📋 Phase 9: Multi-Level Security System Tests")
        self.test_security_status_api()
        self.test_pin_security_system()
        self.test_sms_security_system()
        self.test_webauthn_biometric_system()
        self.test_security_authentication_requirements()
        self.test_security_different_user_roles()
        
        # Phase 10: Security & Access Control Tests
        print("\n📋 Phase 10: Security & Access Control Tests")
        self.test_role_based_access_control()
        self.test_error_handling()
        
        # Phase 11: Customer Deletion Tests
        print("\n📋 Phase 11: Customer Deletion Tests")
        self.test_delete_customer_with_orders()
        self.test_delete_customer_without_orders()
        
        # Phase 12: Cleanup Tests
        print("\n📋 Phase 12: Cleanup Tests")
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
    import sys
    tester = DeliveryManagementAPITester()
    
    # Check if we should run focused tests or all tests
    if len(sys.argv) > 1 and sys.argv[1] == "focused":
        success = tester.run_farmygo_order_visibility_tests()
    else:
        success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())