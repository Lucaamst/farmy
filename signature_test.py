#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class SignatureSystemTester:
    def __init__(self, base_url="https://courier-hub-32.preview.emergentagent.com"):
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
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

    def setup_test_environment(self):
        """Set up test environment with company, admin, and courier"""
        print("🔧 Setting up test environment...")
        
        # 1. Login as super admin
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": "superadmin", "password": "admin123"},
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to login as super admin: {status}")
            return False
        
        self.tokens['super_admin'] = response['access_token']
        
        # 2. Create test company
        timestamp = datetime.now().strftime('%H%M%S')
        company_data = {
            "name": f"SignatureTest_Company_{timestamp}",
            "admin_username": f"sig_admin_{timestamp}",
            "admin_password": "SigTest123!"
        }
        
        success, status, response = self.make_request(
            'POST', 'companies',
            data=company_data,
            token=self.tokens['super_admin'],
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to create company: {status}")
            return False
        
        self.test_data['company'] = response['company']
        self.test_data['company_admin_creds'] = {
            'username': company_data['admin_username'],
            'password': company_data['admin_password']
        }
        
        # 3. Login as company admin
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data=self.test_data['company_admin_creds'],
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to login as company admin: {status}")
            return False
        
        self.tokens['company_admin'] = response['access_token']
        
        # 4. Create courier
        courier_data = {
            "username": f"sig_courier_{timestamp}",
            "password": "SigCourier123!",
            "full_name": "Mario Signature Tester"
        }
        
        success, status, response = self.make_request(
            'POST', 'couriers',
            data=courier_data,
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to create courier: {status}")
            return False
        
        self.test_data['courier_creds'] = courier_data
        
        # 5. Get courier ID
        success, status, response = self.make_request(
            'GET', 'couriers',
            token=self.tokens['company_admin'],
            expected_status=200
        )
        
        if not success or not response:
            print(f"❌ Failed to get couriers: {status}")
            return False
        
        self.test_data['courier_id'] = response[0]['id']
        
        # 6. Login as courier
        success, status, response = self.make_request(
            'POST', 'auth/login',
            data={"username": courier_data['username'], "password": courier_data['password']},
            expected_status=200
        )
        
        if not success:
            print(f"❌ Failed to login as courier: {status}")
            return False
        
        self.tokens['courier'] = response['access_token']
        
        print("✅ Test environment setup complete")
        return True

    def test_order_creation_with_signature_requirement(self):
        """Test creating orders with and without signature requirement"""
        print("\n✍️ Testing Order Creation with Signature Requirement")
        
        # Test 1: Create order WITH signature requirement
        order_with_sig_data = {
            "customer_name": "Luca Rossi",
            "delivery_address": "Via Firenze 25, Roma, 00185 RM",
            "phone_number": "+39 333 7777777",
            "reference_number": "SIG-REQ-001",
            "requires_signature": True
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=order_with_sig_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success1 and 'order' in response1:
            self.test_data['signature_order'] = response1['order']
            requires_sig_correct = response1['order'].get('requires_signature') == True
        else:
            requires_sig_correct = False
        
        # Test 2: Create order WITHOUT signature requirement
        order_no_sig_data = {
            "customer_name": "Anna Bianchi",
            "delivery_address": "Via Milano 30, Roma, 00186 RM",
            "phone_number": "+39 333 8888888",
            "reference_number": "NO-SIG-001",
            "requires_signature": False
        }
        
        success2, status2, response2 = self.make_request(
            'POST', 'orders',
            data=order_no_sig_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success2 and 'order' in response2:
            self.test_data['no_signature_order'] = response2['order']
            no_sig_correct = response2['order'].get('requires_signature') == False
        else:
            no_sig_correct = False
        
        overall_success = success1 and success2 and requires_sig_correct and no_sig_correct
        
        if overall_success:
            return self.log_test("Order Creation with Signature Requirement", True, 
                               f"- Order with signature: ✅, Order without signature: ✅")
        else:
            details = f"- With sig: {success1} ({status1}), Without sig: {success2} ({status2}), Sig field: {requires_sig_correct}, No sig field: {no_sig_correct}"
            return self.log_test("Order Creation with Signature Requirement", False, details)

    def test_delivery_completion_with_signature(self):
        """Test delivery completion with various signature scenarios"""
        print("\n📝 Testing Delivery Completion with Signature")
        
        # Assign both orders to courier first
        assign_data1 = {
            "order_id": self.test_data['signature_order']['id'],
            "courier_id": self.test_data['courier_id']
        }
        
        assign_data2 = {
            "order_id": self.test_data['no_signature_order']['id'],
            "courier_id": self.test_data['courier_id']
        }
        
        success_assign1, _, _ = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data1,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        success_assign2, _, _ = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_data2,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not (success_assign1 and success_assign2):
            return self.log_test("Delivery Completion with Signature", False, "- Failed to assign orders to courier")
        
        # Sample base64 signature image (small PNG)
        sample_signature = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Test 1: Complete delivery WITH signature data (signature required order)
        complete_with_sig_data = {
            "order_id": self.test_data['signature_order']['id'],
            "signature_data": sample_signature,
            "signed_by_name": "Luca Rossi",
            "delivery_comment": "Consegna completata con firma digitale"
        }
        
        success1, status1, response1 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_with_sig_data,
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        # Test 2: Complete delivery WITHOUT signature data (no signature required order)
        complete_no_sig_data = {
            "order_id": self.test_data['no_signature_order']['id'],
            "delivery_comment": "Consegna completata senza firma richiesta"
        }
        
        success2, status2, response2 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_no_sig_data,
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        # Test 3: Try to complete signature-required order WITHOUT signature (should fail)
        test_order_data = {
            "customer_name": "Test Signature Required",
            "delivery_address": "Via Test 1, Roma, 00100 RM",
            "phone_number": "+39 333 9999999",
            "reference_number": "TEST-SIG-REQ",
            "requires_signature": True
        }
        
        success3a, status3a, response3a = self.make_request(
            'POST', 'orders',
            data=test_order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success3a and 'order' in response3a:
            test_order_id = response3a['order']['id']
            
            # Assign to courier
            assign_test_data = {
                "order_id": test_order_id,
                "courier_id": self.test_data['courier_id']
            }
            
            success3b, _, _ = self.make_request(
                'PATCH', 'orders/assign',
                data=assign_test_data,
                token=self.tokens.get('company_admin'),
                expected_status=200
            )
            
            if success3b:
                # Try to complete without signature (should fail)
                complete_fail_data = {
                    "order_id": test_order_id,
                    "delivery_comment": "Tentativo senza firma"
                }
                
                success3, status3, response3 = self.make_request(
                    'PATCH', 'courier/deliveries/mark-delivered',
                    data=complete_fail_data,
                    token=self.tokens.get('courier'),
                    expected_status=400
                )
                
                # Test 4: Complete with signature_skipped flag
                complete_skipped_data = {
                    "order_id": test_order_id,
                    "signature_skipped": True,
                    "delivery_comment": "Firma saltata per motivi tecnici"
                }
                
                success4, status4, response4 = self.make_request(
                    'PATCH', 'courier/deliveries/mark-delivered',
                    data=complete_skipped_data,
                    token=self.tokens.get('courier'),
                    expected_status=200
                )
            else:
                success3 = False
                success4 = False
        else:
            success3 = False
            success4 = False
        
        overall_success = success1 and success2 and success3 and success4
        
        if overall_success:
            return self.log_test("Delivery Completion with Signature", True, 
                               f"- With signature: ✅, Without signature: ✅, Missing signature blocked: ✅, Signature skipped: ✅")
        else:
            details = f"- With sig: {success1} ({status1}), Without sig: {success2} ({status2}), Missing blocked: {success3}, Skipped: {success4}"
            return self.log_test("Delivery Completion with Signature", False, details)

    def test_pdf_generation(self):
        """Test PDF generation for delivery confirmation"""
        print("\n📄 Testing PDF Generation")
        
        # Test 1: Generate PDF for delivered order with signature
        signature_order_id = self.test_data['signature_order']['id']
        
        success1, status1, response1 = self.make_request(
            'GET', f'orders/{signature_order_id}/delivery-confirmation-pdf',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Verify PDF response
        pdf_correct = False
        if success1 and isinstance(response1, dict):
            content_type = response1.get('content_type', '')
            content_length = response1.get('content_length', 0)
            is_binary = response1.get('is_binary', False)
            
            pdf_correct = (
                'application/pdf' in content_type and
                content_length > 0 and
                is_binary
            )
        
        # Test 2: Generate PDF for delivered order without signature
        no_sig_order_id = self.test_data['no_signature_order']['id']
        
        success2, status2, response2 = self.make_request(
            'GET', f'orders/{no_sig_order_id}/delivery-confirmation-pdf',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        # Verify PDF response for no signature order
        pdf_no_sig_correct = False
        if success2 and isinstance(response2, dict):
            content_type = response2.get('content_type', '')
            content_length = response2.get('content_length', 0)
            is_binary = response2.get('is_binary', False)
            
            pdf_no_sig_correct = (
                'application/pdf' in content_type and
                content_length > 0 and
                is_binary
            )
        
        # Test 3: Try to generate PDF for non-delivered order (should fail)
        pending_order_data = {
            "customer_name": "Pending Order Test",
            "delivery_address": "Via Pending 1, Roma, 00100 RM",
            "phone_number": "+39 333 0000001",
            "reference_number": "PENDING-PDF-TEST",
            "requires_signature": False
        }
        
        success3a, status3a, response3a = self.make_request(
            'POST', 'orders',
            data=pending_order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if success3a and 'order' in response3a:
            pending_order_id = response3a['order']['id']
            
            success3, status3, response3 = self.make_request(
                'GET', f'orders/{pending_order_id}/delivery-confirmation-pdf',
                token=self.tokens.get('company_admin'),
                expected_status=400
            )
        else:
            success3 = False
        
        # Test 4: Try to generate PDF for non-existent order (should fail)
        fake_order_id = "00000000-0000-0000-0000-000000000000"
        
        success4, status4, response4 = self.make_request(
            'GET', f'orders/{fake_order_id}/delivery-confirmation-pdf',
            token=self.tokens.get('company_admin'),
            expected_status=404
        )
        
        overall_success = success1 and pdf_correct and success2 and pdf_no_sig_correct and success3 and success4
        
        if overall_success:
            return self.log_test("PDF Generation", True, 
                               f"- With signature PDF: ✅, Without signature PDF: ✅, Non-delivered blocked: ✅, Non-existent blocked: ✅")
        else:
            details = f"- With sig PDF: {success1}/{pdf_correct}, Without sig PDF: {success2}/{pdf_no_sig_correct}, Non-delivered: {success3} ({status3}), Non-existent: {success4} ({status4})"
            return self.log_test("PDF Generation", False, details)

    def test_signature_integration_workflow(self):
        """Test complete end-to-end signature workflow"""
        print("\n🔄 Testing Signature Integration Workflow")
        
        # Step 1: Company admin creates order with signature requirement
        timestamp = datetime.now().strftime('%H%M%S')
        workflow_order_data = {
            "customer_name": f"Workflow Test Customer {timestamp}",
            "delivery_address": f"Via Workflow {timestamp}, Roma, 00100 RM",
            "phone_number": f"+39 333 {timestamp}",
            "reference_number": f"WORKFLOW-{timestamp}",
            "requires_signature": True
        }
        
        success1, status1, response1 = self.make_request(
            'POST', 'orders',
            data=workflow_order_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success1 or 'order' not in response1:
            return self.log_test("Signature Integration Workflow", False, f"- Failed to create order: {status1}")
        
        workflow_order = response1['order']
        
        # Step 2: Assign order to courier
        assign_workflow_data = {
            "order_id": workflow_order['id'],
            "courier_id": self.test_data['courier_id']
        }
        
        success2, status2, response2 = self.make_request(
            'PATCH', 'orders/assign',
            data=assign_workflow_data,
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        if not success2:
            return self.log_test("Signature Integration Workflow", False, f"- Failed to assign order: {status2}")
        
        # Step 3: Courier marks delivery with signature and comment
        sample_signature = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        complete_workflow_data = {
            "order_id": workflow_order['id'],
            "signature_data": sample_signature,
            "signed_by_name": workflow_order_data['customer_name'],
            "delivery_comment": "Consegna completata con successo. Cliente soddisfatto."
        }
        
        success3, status3, response3 = self.make_request(
            'PATCH', 'courier/deliveries/mark-delivered',
            data=complete_workflow_data,
            token=self.tokens.get('courier'),
            expected_status=200
        )
        
        if not success3:
            return self.log_test("Signature Integration Workflow", False, f"- Failed to complete delivery: {status3}")
        
        # Step 4: Verify order status and signature data are saved
        success4, status4, response4 = self.make_request(
            'GET', 'orders',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        order_updated_correctly = False
        if success4 and isinstance(response4, list):
            for order in response4:
                if order.get('id') == workflow_order['id']:
                    order_updated_correctly = (
                        order.get('status') == 'delivered' and
                        order.get('signature_data') is not None and
                        order.get('signed_by_name') == workflow_order_data['customer_name'] and
                        order.get('signed_at') is not None and
                        order.get('delivery_comment') == "Consegna completata con successo. Cliente soddisfatto." and
                        order.get('commented_by') is not None and
                        order.get('commented_at') is not None
                    )
                    break
        
        # Step 5: Company admin downloads PDF confirmation
        success5, status5, response5 = self.make_request(
            'GET', f'orders/{workflow_order["id"]}/delivery-confirmation-pdf',
            token=self.tokens.get('company_admin'),
            expected_status=200
        )
        
        pdf_generated = False
        if success5 and isinstance(response5, dict):
            content_type = response5.get('content_type', '')
            content_length = response5.get('content_length', 0)
            is_binary = response5.get('is_binary', False)
            
            pdf_generated = (
                'application/pdf' in content_type and
                content_length > 0 and
                is_binary
            )
        
        overall_success = success1 and success2 and success3 and success4 and order_updated_correctly and success5 and pdf_generated
        
        if overall_success:
            return self.log_test("Signature Integration Workflow", True, 
                               f"- Order creation: ✅, Assignment: ✅, Delivery with signature: ✅, Data verification: ✅, PDF generation: ✅")
        else:
            details = f"- Create: {success1}, Assign: {success2}, Complete: {success3}, Verify: {success4}/{order_updated_correctly}, PDF: {success5}/{pdf_generated}"
            return self.log_test("Signature Integration Workflow", False, details)

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
                print("✅ Test company and related data cleaned up")
            else:
                print(f"❌ Failed to clean up test company: {status}")

    def run_signature_tests(self):
        """Run all signature system tests"""
        print("🚀 Starting Digital Signature System Tests")
        print("=" * 60)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        # Run signature tests
        print("\n📋 Digital Signature System Tests")
        self.test_order_creation_with_signature_requirement()
        self.test_delivery_completion_with_signature()
        self.test_pdf_generation()
        self.test_signature_integration_workflow()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Digital Signature System tests passed!")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed. Check the issues above.")
            return False

if __name__ == "__main__":
    tester = SignatureSystemTester()
    success = tester.run_signature_tests()
    sys.exit(0 if success else 1)