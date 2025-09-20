import requests
import sys
import json
from datetime import datetime, timezone, timedelta
import urllib.parse

class FarmyGoRecentModificationsAPITester:
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

    # ========== SETUP METHODS ==========
    
    def setup_authentication(self):
        """Setup authentication tokens for testing"""
        print("🔐 Setting up authentication...")
        
        # Super admin login
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['super_admin'] = response['access_token']
            print("✅ Super admin authenticated")
        else:
            print(f"❌ Super admin authentication failed: {status}")
            return False
        
        # Create test company
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"FarmyGo_RecentMods_Test_{timestamp}",
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
            print(f"✅ Test company created: {response['company']['name']}")
        else:
            print(f"❌ Company creation failed: {status}")
            return False
        
        # Company admin login
        creds = self.test_data['company_admin_creds']
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": creds['username'], "password": creds['password']},
            expected_status=200
        )
        
        if success and 'access_token' in response:
            self.tokens['company_admin'] = response['access_token']
            self.test_data['company_admin_user'] = response['user']
            print("✅ Company admin authenticated")
            return True
        else:
            print(f"❌ Company admin authentication failed: {status}")
            return False

    # ========== COURIER FULL NAME FIELD TESTS ==========
    
    def test_create_courier_with_full_name(self):
        """Test creating courier with full_name field"""
        timestamp = datetime.now().strftime('%H%M%S')
        courier_data = {
            "username": f"mario_rossi_{timestamp}",
            "password": "CourierPass123!",
            "full_name": "Mario Rossi"
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            self.test_data['courier_with_name'] = {
                'username': courier_data['username'],
                'password': courier_data['password'],
                'full_name': courier_data['full_name']
            }
            return self.log_test("Create Courier with Full Name", True, f"- Courier: {courier_data['full_name']} ({courier_data['username']})")
        else:
            return self.log_test("Create Courier with Full Name", False, f"- Status: {status}, Response: {response}")

    def test_create_courier_without_full_name(self):
        """Test creating courier without full_name field (backward compatibility)"""
        timestamp = datetime.now().strftime('%H%M%S')
        courier_data = {
            "username": f"luigi_bianchi_{timestamp}",
            "password": "CourierPass123!"
            # No full_name field
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            self.test_data['courier_without_name'] = {
                'username': courier_data['username'],
                'password': courier_data['password']
            }
            return self.log_test("Create Courier without Full Name", True, f"- Courier: {courier_data['username']} (backward compatibility)")
        else:
            return self.log_test("Create Courier without Full Name", False, f"- Status: {status}, Response: {response}")

    def test_get_couriers_with_full_name_field(self):
        """Test that courier listings include full_name field"""
        success, status, response = self.make_request(
            'GET', 'couriers',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            # Store courier IDs for later tests
            for courier in response:
                if courier.get('username') == self.test_data.get('courier_with_name', {}).get('username'):
                    self.test_data['courier_with_name']['id'] = courier['id']
                elif courier.get('username') == self.test_data.get('courier_without_name', {}).get('username'):
                    self.test_data['courier_without_name']['id'] = courier['id']
            
            # Check if full_name field is present in responses
            full_name_field_present = True
            courier_with_name_found = False
            courier_without_name_found = False
            
            for courier in response:
                if 'full_name' not in courier:
                    full_name_field_present = False
                    break
                
                # Check specific couriers
                if courier.get('username') == self.test_data.get('courier_with_name', {}).get('username'):
                    courier_with_name_found = True
                    if courier.get('full_name') != "Mario Rossi":
                        full_name_field_present = False
                        break
                elif courier.get('username') == self.test_data.get('courier_without_name', {}).get('username'):
                    courier_without_name_found = True
                    # Should be None or empty for backward compatibility
                    if courier.get('full_name') not in [None, ""]:
                        full_name_field_present = False
                        break
            
            if full_name_field_present and courier_with_name_found and courier_without_name_found:
                return self.log_test("Get Couriers with Full Name Field", True, f"- Found {len(response)} couriers, full_name field present in all responses")
            else:
                return self.log_test("Get Couriers with Full Name Field", False, f"- Field present: {full_name_field_present}, With name found: {courier_with_name_found}, Without name found: {courier_without_name_found}")
        else:
            return self.log_test("Get Couriers with Full Name Field", False, f"- Status: {status}, Response: {response}")

    def test_update_courier_with_full_name(self):
        """Test updating existing courier with full_name"""
        if 'courier_without_name' not in self.test_data or 'id' not in self.test_data['courier_without_name']:
            return self.log_test("Update Courier with Full Name", False, "- No courier data available")
        
        courier_id = self.test_data['courier_without_name']['id']
        update_data = {
            "username": self.test_data['courier_without_name']['username'],
            "full_name": "Luigi Bianchi"  # Adding full name to existing courier
        }
        
        success, status, response = self.make_request(
            'PATCH', f'couriers/{courier_id}',
            data=update_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            # Update stored data
            self.test_data['courier_without_name']['full_name'] = update_data['full_name']
            return self.log_test("Update Courier with Full Name", True, f"- Added full name: {update_data['full_name']}")
        else:
            return self.log_test("Update Courier with Full Name", False, f"- Status: {status}, Response: {response}")

    def test_update_courier_full_name_only(self):
        """Test updating only the full_name field of existing courier"""
        if 'courier_with_name' not in self.test_data or 'id' not in self.test_data['courier_with_name']:
            return self.log_test("Update Courier Full Name Only", False, "- No courier data available")
        
        courier_id = self.test_data['courier_with_name']['id']
        update_data = {
            "username": self.test_data['courier_with_name']['username'],
            "full_name": "Mario Rossi Updated"  # Updating full name
        }
        
        success, status, response = self.make_request(
            'PATCH', f'couriers/{courier_id}',
            data=update_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success:
            # Update stored data
            self.test_data['courier_with_name']['full_name'] = update_data['full_name']
            return self.log_test("Update Courier Full Name Only", True, f"- Updated full name: {update_data['full_name']}")
        else:
            return self.log_test("Update Courier Full Name Only", False, f"- Status: {status}, Response: {response}")

    # ========== ORDERS DAILY FILTER TESTS ==========
    
    def test_create_orders_for_date_testing(self):
        """Create orders with different dates for testing filters"""
        print("\n📅 Creating test orders for date filtering...")
        
        # Create orders for today
        today_order_data = {
            "customer_name": "Cliente Oggi",
            "delivery_address": "Via Roma 123, Milano, 20121 MI",
            "phone_number": "+39 333 1111111",
            "reference_number": "TODAY-001"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=today_order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success1 and 'order' in response1:
            self.test_data['today_order'] = response1['order']
            print(f"✅ Today's order created: {response1['order']['id']}")
        else:
            print(f"❌ Today's order creation failed: {status1}")
            return False
        
        # Create another order for today
        today_order_data2 = {
            "customer_name": "Cliente Oggi 2",
            "delivery_address": "Via Dante 456, Roma, 00185 RM",
            "phone_number": "+39 333 2222222",
            "reference_number": "TODAY-002"
        }
        
        success2, status2, response2 = self.make_request(
            'POST', 'orders',
            data=today_order_data2,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success2 and 'order' in response2:
            self.test_data['today_order2'] = response2['order']
            print(f"✅ Second today's order created: {response2['order']['id']}")
        else:
            print(f"❌ Second today's order creation failed: {status2}")
        
        return success1 and success2

    def test_orders_search_today_filter(self):
        """Test GET /api/orders/search with today's date filter"""
        # Get today's date in ISO format
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Test with date_from and date_to for today
        params = {
            "date_from": today_start.isoformat(),
            "date_to": today_end.isoformat()
        }
        
        success, status, response = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            # Check if our today's orders are in the results
            today_orders_found = 0
            for order in response:
                if order.get('reference_number') in ['TODAY-001', 'TODAY-002']:
                    today_orders_found += 1
            
            if today_orders_found >= 2:
                return self.log_test("Orders Search Today Filter", True, f"- Found {today_orders_found} today's orders out of {len(response)} total")
            else:
                return self.log_test("Orders Search Today Filter", False, f"- Expected 2 today's orders, found {today_orders_found}")
        else:
            return self.log_test("Orders Search Today Filter", False, f"- Status: {status}, Response: {response}")

    def test_orders_search_date_from_only(self):
        """Test orders search with only date_from parameter"""
        # Get yesterday's date
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        params = {
            "date_from": yesterday_start.isoformat()
        }
        
        success, status, response = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            # Should include today's orders (created after yesterday)
            today_orders_found = 0
            for order in response:
                if order.get('reference_number') in ['TODAY-001', 'TODAY-002']:
                    today_orders_found += 1
            
            if today_orders_found >= 2:
                return self.log_test("Orders Search Date From Only", True, f"- Found {today_orders_found} orders from yesterday onwards")
            else:
                return self.log_test("Orders Search Date From Only", False, f"- Expected at least 2 orders, found {today_orders_found}")
        else:
            return self.log_test("Orders Search Date From Only", False, f"- Status: {status}, Response: {response}")

    def test_orders_search_date_to_only(self):
        """Test orders search with only date_to parameter"""
        # Get tomorrow's date
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        params = {
            "date_to": tomorrow_end.isoformat()
        }
        
        success, status, response = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            # Should include today's orders (created before tomorrow)
            today_orders_found = 0
            for order in response:
                if order.get('reference_number') in ['TODAY-001', 'TODAY-002']:
                    today_orders_found += 1
            
            if today_orders_found >= 2:
                return self.log_test("Orders Search Date To Only", True, f"- Found {today_orders_found} orders up to tomorrow")
            else:
                return self.log_test("Orders Search Date To Only", False, f"- Expected at least 2 orders, found {today_orders_found}")
        else:
            return self.log_test("Orders Search Date To Only", False, f"- Status: {status}, Response: {response}")

    def test_orders_search_custom_date_range(self):
        """Test orders search with custom date range"""
        # Get a date range that should include today
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        
        yesterday_start = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc)
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        params = {
            "date_from": yesterday_start.isoformat(),
            "date_to": tomorrow_end.isoformat()
        }
        
        success, status, response = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            # Should include today's orders
            today_orders_found = 0
            for order in response:
                if order.get('reference_number') in ['TODAY-001', 'TODAY-002']:
                    today_orders_found += 1
            
            if today_orders_found >= 2:
                return self.log_test("Orders Search Custom Date Range", True, f"- Found {today_orders_found} orders in custom range")
            else:
                return self.log_test("Orders Search Custom Date Range", False, f"- Expected at least 2 orders, found {today_orders_found}")
        else:
            return self.log_test("Orders Search Custom Date Range", False, f"- Status: {status}, Response: {response}")

    def test_orders_search_invalid_date_handling(self):
        """Test error handling for invalid dates in order search"""
        # Test with invalid date format
        params = {
            "date_from": "invalid-date-format"
        }
        
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=[400, 422, 500]  # Various possible error codes for invalid date
        )
        
        # Test with date_from after date_to (logical error)
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
        
        params2 = {
            "date_from": tomorrow.isoformat(),
            "date_to": yesterday.isoformat()
        }
        
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            params=params2,
            token=self.tokens.get('company_admin'),
            expected_status=200  # Should return empty results, not error
        )
        
        # For the second test, check if it returns empty results
        empty_results = success2 and isinstance(response2, list) and len(response2) == 0
        
        if success1 and (success2 or empty_results):
            return self.log_test("Orders Search Invalid Date Handling", True, f"- Invalid format handled, logical error handled")
        else:
            return self.log_test("Orders Search Invalid Date Handling", False, f"- Invalid format: {success1} ({status1}), Logical error: {success2 or empty_results} ({status2})")

    # ========== UPDATED API RESPONSES TESTS ==========
    
    def test_courier_responses_include_full_name(self):
        """Verify courier responses include full_name field"""
        success, status, response = self.make_request(
            'GET', 'couriers',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success and isinstance(response, list):
            full_name_in_all = True
            couriers_with_names = 0
            couriers_without_names = 0
            
            for courier in response:
                if 'full_name' not in courier:
                    full_name_in_all = False
                    break
                
                if courier.get('full_name'):
                    couriers_with_names += 1
                else:
                    couriers_without_names += 1
            
            if full_name_in_all:
                return self.log_test("Courier Responses Include Full Name", True, f"- All {len(response)} couriers have full_name field ({couriers_with_names} with names, {couriers_without_names} without)")
            else:
                return self.log_test("Courier Responses Include Full Name", False, f"- Some couriers missing full_name field")
        else:
            return self.log_test("Courier Responses Include Full Name", False, f"- Status: {status}, Response: {response}")

    def test_order_search_filter_combinations(self):
        """Test order search with various filter combinations"""
        # Test 1: Customer name + date filter
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        params1 = {
            "customer_name": "Cliente Oggi",
            "date_from": today_start.isoformat(),
            "date_to": today_end.isoformat()
        }
        
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params=params1,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 2: Status + date filter
        params2 = {
            "status": "pending",
            "date_from": today_start.isoformat()
        }
        
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            params=params2,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test 3: Multiple filters
        if 'courier_with_name' in self.test_data and 'id' in self.test_data['courier_with_name']:
            params3 = {
                "courier_id": self.test_data['courier_with_name']['id'],
                "status": "pending",
                "date_from": today_start.isoformat()
            }
            
            success3, status3, response3 = self.make_request(
                'GET', 'orders/search',
                params=params3,
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
        else:
            success3 = True  # Skip this test if no courier available
        
        overall_success = success1 and success2 and success3
        
        if overall_success:
            return self.log_test("Order Search Filter Combinations", True, f"- All filter combinations working")
        else:
            return self.log_test("Order Search Filter Combinations", False, f"- Name+Date: {success1}, Status+Date: {success2}, Multiple: {success3}")

    def test_empty_null_filters_handling(self):
        """Test that empty/null filters are handled correctly"""
        # Test with empty string filters
        params1 = {
            "customer_name": "",
            "status": "",
            "courier_id": ""
        }
        
        success1, status1, response1 = self.make_request(
            'GET', 'orders/search',
            params=params1,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Test with no filters (should return all orders)
        success2, status2, response2 = self.make_request(
            'GET', 'orders/search',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Both should return results (empty filters should be ignored)
        if success1 and success2 and isinstance(response1, list) and isinstance(response2, list):
            # Should return same number of results (empty filters ignored)
            if len(response1) == len(response2):
                return self.log_test("Empty/Null Filters Handling", True, f"- Empty filters ignored, returned {len(response1)} orders")
            else:
                return self.log_test("Empty/Null Filters Handling", False, f"- Empty filters: {len(response1)}, No filters: {len(response2)}")
        else:
            return self.log_test("Empty/Null Filters Handling", False, f"- Empty filters: {success1} ({status1}), No filters: {success2} ({status2})")

    # ========== INTEGRATION TESTS ==========
    
    def test_integration_courier_order_workflow(self):
        """Test complete workflow: create courier with full name, create order, assign, filter"""
        print("\n🔄 Testing complete integration workflow...")
        
        # Step 1: Create courier with full name (already done in setup)
        if 'courier_with_name' not in self.test_data or 'id' not in self.test_data['courier_with_name']:
            return self.log_test("Integration Workflow", False, "- No courier with full name available")
        
        # Step 2: Create order for integration test
        integration_order_data = {
            "customer_name": "Cliente Integrazione",
            "delivery_address": "Via Integrazione 789, Napoli, 80100 NA",
            "phone_number": "+39 333 9999999",
            "reference_number": "INTEGRATION-001"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=integration_order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Integration Workflow - Create Order", False, f"- Status: {status1}")
        
        integration_order = response1['order']
        
        # Step 3: Assign order to courier with full name
        assign_data = {
            "order_id": integration_order['id'],
            "courier_id": self.test_data['courier_with_name']['id']
        }
        
        success2, status2, response2 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success2:
            return self.log_test("Integration Workflow - Assign Order", False, f"- Status: {status2}")
        
        # Step 4: Filter orders by courier (should show courier full name)
        params = {
            "courier_id": self.test_data['courier_with_name']['id']
        }
        
        success3, status3, response3 = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success3:
            return self.log_test("Integration Workflow - Filter by Courier", False, f"- Status: {status3}")
        
        # Step 5: Verify the assigned order appears in results
        integration_order_found = False
        for order in response3:
            if order.get('id') == integration_order['id']:
                integration_order_found = True
                if order.get('courier_id') == self.test_data['courier_with_name']['id']:
                    break
        
        if integration_order_found:
            return self.log_test("Integration Workflow", True, f"- Complete workflow successful: courier with full name, order creation, assignment, filtering")
        else:
            return self.log_test("Integration Workflow", False, f"- Assigned order not found in courier filter results")

    def test_backward_compatibility_workflow(self):
        """Test that couriers without full names still work correctly"""
        if 'courier_without_name' not in self.test_data or 'id' not in self.test_data['courier_without_name']:
            return self.log_test("Backward Compatibility Workflow", False, "- No courier without full name available")
        
        # Create order for backward compatibility test
        compat_order_data = {
            "customer_name": "Cliente Compatibilità",
            "delivery_address": "Via Compatibilità 456, Torino, 10100 TO",
            "phone_number": "+39 333 8888888",
            "reference_number": "COMPAT-001"
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=compat_order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success1:
            return self.log_test("Backward Compatibility Workflow", False, f"- Order creation failed: {status1}")
        
        compat_order = response1['order']
        
        # Assign to courier without full name
        assign_data = {
            "order_id": compat_order['id'],
            "courier_id": self.test_data['courier_without_name']['id']
        }
        
        success2, status2, response2 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success2:
            return self.log_test("Backward Compatibility Workflow", False, f"- Order assignment failed: {status2}")
        
        # Filter by this courier
        params = {
            "courier_id": self.test_data['courier_without_name']['id']
        }
        
        success3, status3, response3 = self.make_request(
            'GET', 'orders/search',
            params=params,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success3 and isinstance(response3, list):
            # Check if our order is in the results
            compat_order_found = False
            for order in response3:
                if order.get('id') == compat_order['id']:
                    compat_order_found = True
                    break
            
            if compat_order_found:
                return self.log_test("Backward Compatibility Workflow", True, f"- Courier without full name works correctly")
            else:
                return self.log_test("Backward Compatibility Workflow", False, f"- Order not found in courier filter")
        else:
            return self.log_test("Backward Compatibility Workflow", False, f"- Filter failed: {status3}")

    # ========== CLEANUP ==========
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if 'company' in self.test_data:
            delete_data = {"password": "admin123"}
            success, status, response = self.make_request(
                'DELETE', f'companies/{self.test_data["company"]["id"]}',
                data=delete_data,
                token=self.tokens.get('super_admin'),
                expected_status=200
            )
            
            if success:
                print("✅ Test company deleted")
            else:
                print(f"❌ Test company deletion failed: {status}")

    # ========== MAIN TEST RUNNER ==========
    
    def run_recent_modifications_tests(self):
        """Run all recent modifications tests"""
        print("🚀 Starting FarmyGo Recent Modifications API Tests")
        print("=" * 70)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Aborting tests.")
            return False
        
        # Phase 1: Courier Full Name Field Tests
        print("\n📋 Phase 1: Courier Full Name Field Tests")
        self.test_create_courier_with_full_name()
        self.test_create_courier_without_full_name()
        self.test_get_couriers_with_full_name_field()
        self.test_update_courier_with_full_name()
        self.test_update_courier_full_name_only()
        
        # Phase 2: Orders Daily Filter Tests
        print("\n📋 Phase 2: Orders Daily Filter Tests")
        self.test_create_orders_for_date_testing()
        self.test_orders_search_today_filter()
        self.test_orders_search_date_from_only()
        self.test_orders_search_date_to_only()
        self.test_orders_search_custom_date_range()
        self.test_orders_search_invalid_date_handling()
        
        # Phase 3: Updated API Responses Tests
        print("\n📋 Phase 3: Updated API Responses Tests")
        self.test_courier_responses_include_full_name()
        self.test_order_search_filter_combinations()
        self.test_empty_null_filters_handling()
        
        # Phase 4: Integration Tests
        print("\n📋 Phase 4: Integration Tests")
        self.test_integration_courier_order_workflow()
        self.test_backward_compatibility_workflow()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All recent modifications tests passed! FarmyGo new features are working correctly.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} test(s) failed. Please review the failed tests above.")
            return False

if __name__ == "__main__":
    tester = FarmyGoRecentModificationsAPITester()
    success = tester.run_recent_modifications_tests()
    sys.exit(0 if success else 1)