from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import json
import base64

# WebAuthn imports (will be imported dynamically in functions to avoid dependency issues)
try:
    import webauthn
    WEBAUTHN_AVAILABLE = True
except ImportError:
    WEBAUTHN_AVAILABLE = False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# User roles
class UserRole:
    SUPER_ADMIN = "super_admin"
    COMPANY_ADMIN = "company_admin"
    COURIER = "courier"

# Pydantic Models
class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_deliveries: int = 0
    active_couriers: int = 0

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    full_name: Optional[str] = None  # Added full name field
    role: str
    company_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    delivery_address: str
    phone_number: str
    reference_number: Optional[str] = None
    company_id: str
    courier_id: Optional[str] = None
    customer_id: Optional[str] = None  # Link to customer record
    status: str = "pending"  # pending, assigned, in_progress, delivered
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None
    sms_sent: bool = False

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone_number: str
    address: str
    email: Optional[str] = None
    notes: Optional[str] = None
    company_id: str
    total_orders: int = 0
    last_order_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User
    company: Optional[Company] = None

class CreateCompanyRequest(BaseModel):
    name: str
    admin_username: str
    admin_password: str

class UpdateCompanyRequest(BaseModel):
    name: str

class DeleteCompanyRequest(BaseModel):
    password: str

class ResetCompanyPasswordRequest(BaseModel):
    company_id: str
    new_password: str
    admin_password: str

class CreateCourierRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None

class UpdateCourierRequest(BaseModel):
    username: str
    password: Optional[str] = None
    full_name: Optional[str] = None

class CreateOrderRequest(BaseModel):
    customer_name: str
    delivery_address: str
    phone_number: Optional[str] = None  # Made optional for SMS notifications
    reference_number: Optional[str] = None
    customer_id: Optional[str] = None  # If selecting existing customer

class UpdateOrderRequest(BaseModel):
    customer_name: str
    delivery_address: str
    phone_number: str
    reference_number: Optional[str] = None

class AssignOrderRequest(BaseModel):
    order_id: str
    courier_id: str

class MarkDeliveredRequest(BaseModel):
    order_id: str

class CreateCustomerRequest(BaseModel):
    name: str
    phone_number: str
    address: str
    email: Optional[str] = None
    notes: Optional[str] = None

class UpdateCustomerRequest(BaseModel):
    name: str
    phone_number: str
    address: str
    email: Optional[str] = None
    notes: Optional[str] = None

# Security Models
class UserSecurity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    face_id_enabled: bool = False
    pin_enabled: bool = False
    sms_enabled: bool = False
    pin_hash: Optional[str] = None
    webauthn_credentials: List = Field(default_factory=list)
    backup_codes: List = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SetupPinRequest(BaseModel):
    pin: str

class VerifyPinRequest(BaseModel):
    pin: str

class SendSMSCodeRequest(BaseModel):
    phone_number: str

class VerifySMSCodeRequest(BaseModel):
    phone_number: str
    code: str

class WebAuthnRegistrationRequest(BaseModel):
    credential: dict

class WebAuthnAuthenticationRequest(BaseModel):
    credential: dict

# SMS Cost Tracking Models
class SMSCostSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cost_per_sms: float = 0.05  # Default cost per SMS in EUR
    currency: str = "EUR"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str  # Super admin user ID

class SMSMonthlyStats(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    year: int
    month: int
    total_sms_sent: int = 0
    successful_sms: int = 0
    failed_sms: int = 0
    total_cost: float = 0.0
    cost_per_sms: float = 0.05
    currency: str = "EUR"
    companies_breakdown: dict = Field(default_factory=dict)  # company_id -> count
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UpdateSMSCostRequest(BaseModel):
    cost_per_sms: float
    currency: str = "EUR"

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = await db.users.find_one({"username": username})
        if user_data is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_data)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(required_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# SMS Cost Management Functions
async def get_sms_cost_settings():
    """Get current SMS cost settings"""
    settings = await db.sms_cost_settings.find_one({})
    if not settings:
        # Create default settings
        default_settings = {
            "id": str(uuid.uuid4()),
            "cost_per_sms": 0.05,
            "currency": "EUR", 
            "updated_at": datetime.now(timezone.utc),
            "updated_by": "system"
        }
        await db.sms_cost_settings.insert_one(default_settings)
        return default_settings
    return settings

async def update_monthly_sms_stats(success: bool = True, company_id: str = None):
    """Update monthly SMS statistics"""
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    
    # Get current cost settings
    cost_settings = await get_sms_cost_settings()
    cost_per_sms = cost_settings["cost_per_sms"]
    
    # Find or create monthly record
    monthly_stats = await db.sms_monthly_stats.find_one({"year": year, "month": month})
    
    if not monthly_stats:
        monthly_stats = {
            "id": str(uuid.uuid4()),
            "year": year,
            "month": month,
            "total_sms_sent": 0,
            "successful_sms": 0,
            "failed_sms": 0,
            "total_cost": 0.0,
            "cost_per_sms": cost_per_sms,
            "currency": cost_settings["currency"],
            "companies_breakdown": {},
            "created_at": now,
            "updated_at": now
        }
    
    # Update counters
    monthly_stats["total_sms_sent"] += 1
    if success:
        monthly_stats["successful_sms"] += 1
        monthly_stats["total_cost"] += cost_per_sms
    else:
        monthly_stats["failed_sms"] += 1
    
    # Update company breakdown
    if company_id:
        if company_id not in monthly_stats["companies_breakdown"]:
            monthly_stats["companies_breakdown"][company_id] = {"sent": 0, "success": 0, "failed": 0}
        
        monthly_stats["companies_breakdown"][company_id]["sent"] += 1
        if success:
            monthly_stats["companies_breakdown"][company_id]["success"] += 1
        else:
            monthly_stats["companies_breakdown"][company_id]["failed"] += 1
    
    monthly_stats["updated_at"] = now
    
    # Upsert the record
    await db.sms_monthly_stats.replace_one(
        {"year": year, "month": month},
        monthly_stats,
        upsert=True
    )

# Security helper functions
def hash_pin(pin: str) -> str:
    """Hash PIN for secure storage"""
    return pwd_context.hash(pin)

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verify PIN against hash"""
    return pwd_context.verify(plain_pin, hashed_pin)

def generate_sms_code() -> str:
    """Generate 6-digit SMS verification code"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

# SMS codes storage (in production, use Redis or database with TTL)
sms_codes = {}

async def get_user_security(user_id: str):
    """Get or create user security settings"""
    security = await db.user_security.find_one({"user_id": user_id})
    if not security:
        # Create default security settings
        new_security = UserSecurity(user_id=user_id)
        await db.user_security.insert_one(new_security.dict())
        return new_security
    return UserSecurity(**security)

async def send_sms_notification(phone_number: str, message: str):
    """Send SMS notification using Twilio"""
    try:
        # Initialize Twilio client
        from twilio.rest import Client
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print(f"⚠️ Twilio credentials not found, using mock SMS")
            print(f"MOCK SMS to {phone_number}: {message}")
        else:
            client = Client(account_sid, auth_token)
            
            # Send SMS via Twilio
            message_obj = client.messages.create(
                body=message,
                from_='+15005550006',  # Twilio test number - you can replace with your Twilio number
                to=phone_number
            )
            
            print(f"✅ SMS sent via Twilio to {phone_number}, SID: {message_obj.sid}")
        
        # Store SMS log
        sms_log = {
            "id": str(uuid.uuid4()),
            "phone_number": phone_number,
            "message": message,
            "sent_at": datetime.now(timezone.utc),
            "status": "sent",
            "method": "twilio" if account_sid and auth_token else "mock"
        }
        await db.sms_logs.insert_one(sms_log)
        return True
        
    except Exception as e:
        print(f"❌ SMS sending failed: {str(e)}")
        # Store failed SMS log
        sms_log = {
            "id": str(uuid.uuid4()),
            "phone_number": phone_number,
            "message": message,
            "sent_at": datetime.now(timezone.utc),
            "status": "failed",
            "error": str(e),
            "method": "twilio"
        }
        await db.sms_logs.insert_one(sms_log)
        return False

# Initialize super admin
async def init_super_admin():
    existing_admin = await db.users.find_one({"role": UserRole.SUPER_ADMIN})
    if not existing_admin:
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "superadmin",
            "password": hash_password("admin123"),
            "role": UserRole.SUPER_ADMIN,
            "company_id": None,
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(admin_user)
        print("Super admin created: username=superadmin, password=admin123")

# Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user_data = await db.users.find_one({"username": request.username})
    if not user_data or not verify_password(request.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user_data["is_active"]:
        raise HTTPException(status_code=401, detail="Account disabled")
    
    access_token = create_access_token({"sub": user_data["username"]})
    user = User(**user_data)
    
    company = None
    if user.company_id:
        company_data = await db.companies.find_one({"id": user.company_id})
        if company_data:
            company = Company(**company_data)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
        company=company
    )

# Super Admin Routes
@api_router.post("/companies")
async def create_company(
    request: CreateCompanyRequest,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    # Check if company name exists
    existing_company = await db.companies.find_one({"name": request.name})
    if existing_company:
        raise HTTPException(status_code=400, detail="Company name already exists")
    
    # Check if admin username exists
    existing_user = await db.users.find_one({"username": request.admin_username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create company
    company = Company(name=request.name)
    await db.companies.insert_one(company.dict())
    
    # Create company admin
    admin_user = {
        "id": str(uuid.uuid4()),
        "username": request.admin_username,
        "password": hash_password(request.admin_password),
        "role": UserRole.COMPANY_ADMIN,
        "company_id": company.id,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(admin_user)
    
    return {"message": "Company and admin created successfully", "company": company}

@api_router.get("/companies", response_model=List[Company])
async def get_companies(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    companies = await db.companies.find().to_list(1000)
    
    # Update statistics for each company
    for company in companies:
        # Count total deliveries
        total_deliveries = await db.orders.count_documents({
            "company_id": company["id"],
            "status": "delivered"
        })
        
        # Count active couriers
        active_couriers = await db.users.count_documents({
            "company_id": company["id"],
            "role": UserRole.COURIER,
            "is_active": True
        })
        
        company["total_deliveries"] = total_deliveries
        company["active_couriers"] = active_couriers
        
        # Update in database
        await db.companies.update_one(
            {"id": company["id"]},
            {"$set": {
                "total_deliveries": total_deliveries,
                "active_couriers": active_couriers
            }}
        )
    
    return [Company(**company) for company in companies]

@api_router.patch("/companies/{company_id}")
async def update_company(
    company_id: str,
    request: UpdateCompanyRequest,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    # Check if company exists
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if new name already exists (excluding current company)
    existing_company = await db.companies.find_one({
        "name": request.name,
        "id": {"$ne": company_id}
    })
    if existing_company:
        raise HTTPException(status_code=400, detail="Company name already exists")
    
    # Update company
    await db.companies.update_one(
        {"id": company_id},
        {"$set": {"name": request.name}}
    )
    
    return {"message": "Company updated successfully"}

@api_router.patch("/companies/{company_id}/reset-password")
async def reset_company_admin_password(
    company_id: str,
    request: ResetCompanyPasswordRequest,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    # Verify super admin password
    admin_user = await db.users.find_one({"id": current_user.id})
    if not admin_user or not verify_password(request.admin_password, admin_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect admin password")
    
    # Find company
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Find company admin
    company_admin = await db.users.find_one({
        "company_id": company_id,
        "role": UserRole.COMPANY_ADMIN
    })
    if not company_admin:
        raise HTTPException(status_code=404, detail="Company admin not found")
    
    # Update password
    await db.users.update_one(
        {"id": company_admin["id"]},
        {"$set": {"password": hash_password(request.new_password)}}
    )
    
    return {"message": "Company admin password reset successfully"}

@api_router.delete("/companies/{company_id}")
async def delete_company(
    company_id: str,
    request: DeleteCompanyRequest,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    # Verify super admin password
    admin_user = await db.users.find_one({"id": current_user.id})
    if not admin_user or not verify_password(request.password, admin_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Check if company exists
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Delete all related data
    await db.orders.delete_many({"company_id": company_id})
    await db.users.delete_many({"company_id": company_id})
    await db.companies.delete_one({"id": company_id})
    
    return {"message": "Company deleted successfully"}

@api_router.patch("/companies/{company_id}/toggle")
async def toggle_company_status(
    company_id: str,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    new_status = not company["is_active"]
    await db.companies.update_one(
        {"id": company_id},
        {"$set": {"is_active": new_status}}
    )
    
    return {"message": f"Company {'enabled' if new_status else 'disabled'}"}

# Company Admin Routes
@api_router.post("/couriers")
async def create_courier(
    request: CreateCourierRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Check if username exists
    existing_user = await db.users.find_one({"username": request.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    courier = {
        "id": str(uuid.uuid4()),
        "username": request.username,
        "password": hash_password(request.password),
        "full_name": request.full_name,
        "role": UserRole.COURIER,
        "company_id": current_user.company_id,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(courier)
    
    return {"message": "Courier created successfully"}

@api_router.get("/couriers", response_model=List[User])
async def get_couriers(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    couriers = await db.users.find({
        "company_id": current_user.company_id,
        "role": UserRole.COURIER
    }).to_list(1000)
    
    return [User(**courier) for courier in couriers]

@api_router.patch("/couriers/{courier_id}")
async def update_courier(
    courier_id: str,
    request: UpdateCourierRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Verify courier belongs to same company
    courier = await db.users.find_one({
        "id": courier_id,
        "company_id": current_user.company_id,
        "role": UserRole.COURIER
    })
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    
    # Check if new username already exists (excluding current courier)
    if request.username != courier["username"]:
        existing_user = await db.users.find_one({
            "username": request.username,
            "id": {"$ne": courier_id}
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Prepare update data
    update_data = {"username": request.username}
    if request.password:
        update_data["password"] = hash_password(request.password)
    if request.full_name is not None:
        update_data["full_name"] = request.full_name
    
    # Update courier
    await db.users.update_one(
        {"id": courier_id},
        {"$set": update_data}
    )
    
    return {"message": "Courier updated successfully"}

@api_router.delete("/couriers/{courier_id}")
async def delete_courier(
    courier_id: str,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Verify courier belongs to same company
    courier = await db.users.find_one({
        "id": courier_id,
        "company_id": current_user.company_id,
        "role": UserRole.COURIER
    })
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    
    # Check if courier has active deliveries
    active_orders = await db.orders.count_documents({
        "courier_id": courier_id,
        "status": {"$in": ["assigned", "in_progress"]}
    })
    if active_orders > 0:
        raise HTTPException(status_code=400, detail="Cannot delete courier with active deliveries")
    
    # Delete courier
    await db.users.delete_one({"id": courier_id})
    
    return {"message": "Courier deleted successfully"}

@api_router.patch("/couriers/{courier_id}/toggle")
async def toggle_courier_status(
    courier_id: str,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    courier = await db.users.find_one({
        "id": courier_id,
        "company_id": current_user.company_id,
        "role": UserRole.COURIER
    })
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    
    new_status = not courier["is_active"]
    await db.users.update_one(
        {"id": courier_id},
        {"$set": {"is_active": new_status}}
    )
    
    return {"message": f"Courier {'activated' if new_status else 'blocked'}"}

@api_router.post("/orders")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # If customer_id is provided, verify it exists and belongs to same company
    customer_id = None
    if request.customer_id:
        customer = await db.customers.find_one({
            "id": request.customer_id,
            "company_id": current_user.company_id
        })
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer_id = request.customer_id
    else:
        # Only check/create customer if phone number is provided
        if request.phone_number:
            # Check if customer with this phone already exists
            existing_customer = await db.customers.find_one({
                "phone_number": request.phone_number,
                "company_id": current_user.company_id
            })
            
            if existing_customer:
                # Use existing customer
                customer_id = existing_customer["id"]
            else:
                # Create new customer automatically (only if phone provided)
                new_customer = Customer(
                    name=request.customer_name,
                    phone_number=request.phone_number,
                    address=request.delivery_address,
                    company_id=current_user.company_id
                )
                await db.customers.insert_one(new_customer.dict())
                customer_id = new_customer.id
    
    order = Order(
        customer_name=request.customer_name,
        delivery_address=request.delivery_address,
        phone_number=request.phone_number or "",  # Store empty string if no phone
        reference_number=request.reference_number,
        company_id=current_user.company_id,
        customer_id=customer_id
    )
    await db.orders.insert_one(order.dict())
    
    return {"message": "Order created successfully", "order": order}

@api_router.get("/orders/search")
async def search_orders(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN])),
    customer_name: Optional[str] = None,
    courier_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None
):
    """Search orders with filters"""
    query = {"company_id": current_user.company_id}
    
    if customer_name:
        query["customer_name"] = {"$regex": customer_name, "$options": "i"}
    
    if courier_id:
        query["courier_id"] = courier_id
    
    if status:
        query["status"] = status
    
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query["created_at"] = date_query
    
    orders = await db.orders.find(query).sort("created_at", -1).to_list(1000)
    return [Order(**order) for order in orders]

@api_router.get("/orders/export")
async def export_orders(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN])),
    customer_name: Optional[str] = None,
    courier_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "excel"
):
    """Export orders to Excel or CSV"""
    # Use same query logic as search
    query = {"company_id": current_user.company_id}
    
    if customer_name:
        query["customer_name"] = {"$regex": customer_name, "$options": "i"}
    
    if courier_id:
        query["courier_id"] = courier_id
    
    if status:
        query["status"] = status
    
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query["created_at"] = date_query
    
    orders = await db.orders.find(query).sort("created_at", -1).to_list(1000)
    
    # Get courier names
    courier_ids = [order.get("courier_id") for order in orders if order.get("courier_id")]
    couriers = await db.users.find({"id": {"$in": courier_ids}}).to_list(1000)
    courier_map = {c["id"]: c["username"] for c in couriers}
    
    # Prepare data for export
    export_data = []
    for order in orders:
        export_data.append({
            "Cliente": order["customer_name"],
            "Indirizzo": order["delivery_address"],
            "Telefono": order["phone_number"],
            "Numero Riferimento": order.get("reference_number", ""),
            "Corriere": courier_map.get(order.get("courier_id"), "Non assegnato"),
            "Stato": order["status"].title(),
            "Data Creazione": order["created_at"].strftime("%d/%m/%Y %H:%M"),
            "Data Consegna": order.get("delivered_at").strftime("%d/%m/%Y %H:%M") if order.get("delivered_at") else ""
        })
    
    if format == "excel":
        import pandas as pd
        import io
        from fastapi.responses import StreamingResponse
        
        df = pd.DataFrame(export_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ordini', index=False)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=ordini.xlsx"}
        )
    else:
        # CSV format
        import csv
        import io
        from fastapi.responses import StreamingResponse
        
        output = io.StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type='text/csv',
            headers={"Content-Disposition": "attachment; filename=ordini.csv"}
        )

@api_router.get("/orders", response_model=List[Order])
async def get_orders(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    orders = await db.orders.find({
        "company_id": current_user.company_id
    }).to_list(1000)
    
    return [Order(**order) for order in orders]

@api_router.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Find order and verify it belongs to same company
    order = await db.orders.find_one({
        "id": order_id,
        "company_id": current_user.company_id
    })
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Don't allow deletion of delivered orders
    if order["status"] == "delivered":
        raise HTTPException(status_code=400, detail="Cannot delete delivered orders")
    
    # Delete order
    await db.orders.delete_one({"id": order_id})
    
    return {"message": "Order deleted successfully"}

@api_router.patch("/orders/assign")
async def assign_order(
    request: AssignOrderRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    print(f"Assign order request: {request}")  # Debug log
    
    # Verify courier belongs to same company
    courier = await db.users.find_one({
        "id": request.courier_id,
        "company_id": current_user.company_id,
        "role": UserRole.COURIER,
        "is_active": True
    })
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found or inactive")
    
    # Find order and verify it belongs to same company
    order = await db.orders.find_one({
        "id": request.order_id,
        "company_id": current_user.company_id
    })
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Don't allow reassignment of delivered orders
    if order["status"] == "delivered":
        raise HTTPException(status_code=400, detail="Cannot reassign delivered orders")
    
    # Update order
    await db.orders.update_one(
        {"id": request.order_id, "company_id": current_user.company_id},
        {"$set": {
            "courier_id": request.courier_id,
            "status": "assigned"
        }}
    )
    
    return {"message": "Order assigned successfully"}

@api_router.patch("/orders/{order_id}")
async def update_order(
    order_id: str,
    request: UpdateOrderRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Find the order and verify it belongs to the same company
    order = await db.orders.find_one({
        "id": order_id,
        "company_id": current_user.company_id
    })
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only allow editing of pending or assigned orders
    if order["status"] not in ["pending", "assigned"]:
        raise HTTPException(status_code=400, detail="Cannot edit orders that are in progress or delivered")
    
    # Update order
    result = await db.orders.update_one(
        {"id": order_id, "company_id": current_user.company_id},
        {"$set": {
            "customer_name": request.customer_name,
            "delivery_address": request.delivery_address,
            "phone_number": request.phone_number,
            "reference_number": request.reference_number
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # If delivery address changed and order is assigned, suggest reassignment
    if (order["delivery_address"] != request.delivery_address and 
        order["status"] == "assigned"):
        return {"message": "Order updated successfully", "suggest_reassignment": True}
    
    return {"message": "Order updated successfully"}

# Customer Routes
@api_router.post("/customers")
async def create_customer(
    request: CreateCustomerRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Check if customer with same phone exists for this company
    existing_customer = await db.customers.find_one({
        "phone_number": request.phone_number,
        "company_id": current_user.company_id
    })
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
    
    customer = Customer(
        name=request.name,
        phone_number=request.phone_number,
        address=request.address,
        email=request.email,
        notes=request.notes,
        company_id=current_user.company_id
    )
    await db.customers.insert_one(customer.dict())
    
    return {"message": "Customer created successfully", "customer": customer}

@api_router.get("/customers", response_model=List[Customer])
async def get_customers(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    customers = await db.customers.find({
        "company_id": current_user.company_id
    }).sort("name", 1).to_list(1000)
    
    # Update customer statistics
    for customer in customers:
        # Count total orders
        total_orders = await db.orders.count_documents({
            "customer_id": customer["id"]
        })
        
        # Get last order date
        last_order = await db.orders.find_one(
            {"customer_id": customer["id"]},
            sort=[("created_at", -1)]
        )
        last_order_date = last_order["created_at"] if last_order else None
        
        # Update customer record
        await db.customers.update_one(
            {"id": customer["id"]},
            {"$set": {
                "total_orders": total_orders,
                "last_order_date": last_order_date,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        customer["total_orders"] = total_orders
        customer["last_order_date"] = last_order_date
    
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/search")
async def search_customers(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN])),
    query: Optional[str] = None
):
    """Search customers by name or phone"""
    search_query = {"company_id": current_user.company_id}
    
    if query:
        search_query["$or"] = [
            {"name": {"$regex": query, "$options": "i"}},
            {"phone_number": {"$regex": query, "$options": "i"}}
        ]
    
    customers = await db.customers.find(search_query).sort("name", 1).to_list(100)
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    customer = await db.customers.find_one({
        "id": customer_id,
        "company_id": current_user.company_id
    })
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return Customer(**customer)

@api_router.patch("/customers/{customer_id}")
async def update_customer(
    customer_id: str,
    request: UpdateCustomerRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Find customer and verify it belongs to same company
    customer = await db.customers.find_one({
        "id": customer_id,
        "company_id": current_user.company_id
    })
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if new phone number already exists (excluding current customer)
    if request.phone_number != customer["phone_number"]:
        existing_customer = await db.customers.find_one({
            "phone_number": request.phone_number,
            "company_id": current_user.company_id,
            "id": {"$ne": customer_id}
        })
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
    
    # Update customer
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {
            "name": request.name,
            "phone_number": request.phone_number,
            "address": request.address,
            "email": request.email,
            "notes": request.notes,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {"message": "Customer updated successfully"}

@api_router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Find customer and verify it belongs to same company
    customer = await db.customers.find_one({
        "id": customer_id,
        "company_id": current_user.company_id
    })
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if customer has orders
    order_count = await db.orders.count_documents({"customer_id": customer_id})
    if order_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete customer with {order_count} orders. Consider archiving instead.")
    
    # Delete customer
    await db.customers.delete_one({"id": customer_id})
    
    return {"message": "Customer deleted successfully"}

@api_router.get("/customers/{customer_id}/orders", response_model=List[Order])
async def get_customer_orders(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Verify customer belongs to same company
    customer = await db.customers.find_one({
        "id": customer_id,
        "company_id": current_user.company_id
    })
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get customer orders
    orders = await db.orders.find({
        "customer_id": customer_id
    }).sort("created_at", -1).to_list(1000)
    
    return [Order(**order) for order in orders]



# Courier Routes
@api_router.get("/courier/deliveries", response_model=List[Order])
async def get_assigned_deliveries(
    current_user: User = Depends(require_role([UserRole.COURIER]))
):
    orders = await db.orders.find({
        "courier_id": current_user.id,
        "status": {"$in": ["assigned", "in_progress"]}
    }).to_list(1000)
    
    return [Order(**order) for order in orders]

@api_router.patch("/courier/deliveries/mark-delivered")
async def mark_delivery_completed(
    request: MarkDeliveredRequest,
    current_user: User = Depends(require_role([UserRole.COURIER]))
):
    # Find the order
    order = await db.orders.find_one({
        "id": request.order_id,
        "courier_id": current_user.id
    })
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] == "delivered":
        raise HTTPException(status_code=400, detail="Order already delivered")
    
    # Update order status
    await db.orders.update_one(
        {"id": request.order_id},
        {"$set": {
            "status": "delivered",
            "delivered_at": datetime.now(timezone.utc),
            "sms_sent": True
        }}
    )
    
    # Send SMS notification only if phone number is provided
    if order["phone_number"] and order["phone_number"].strip():
        message = f"Ciao {order['customer_name']}! 📦 La tua consegna è stata completata con successo all'indirizzo: {order['delivery_address']}. Grazie per aver scelto FarmyGo! 🚚"
        await send_sms_notification(order["phone_number"], message)
    else:
        print(f"📱 SMS skipped for order {request.order_id} - no phone number provided")

    return {"message": "Delivery marked as completed and customer notified"}

@api_router.get("/sms-logs")
async def get_sms_logs(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]))
):
    """Get SMS logs for verification"""
    sms_logs = await db.sms_logs.find().sort("sent_at", -1).to_list(50)
    
    # Convert ObjectId to string for JSON serialization
    for log in sms_logs:
        if '_id' in log:
            log['_id'] = str(log['_id'])
    
    return sms_logs

# Security Routes
@api_router.get("/security/status")
async def get_security_status(current_user: User = Depends(get_current_user)):
    """Get user's security status"""
    security = await get_user_security(current_user.id)
    return {
        "face_id_enabled": security.face_id_enabled,
        "pin_enabled": security.pin_enabled,
        "sms_enabled": security.sms_enabled,
        "webauthn_credentials": len(security.webauthn_credentials)
    }

@api_router.post("/security/setup-pin")
async def setup_pin(
    request: SetupPinRequest,
    current_user: User = Depends(get_current_user)
):
    """Setup or update PIN for user"""
    if len(request.pin) != 6 or not request.pin.isdigit():
        raise HTTPException(status_code=400, detail="PIN must be exactly 6 digits")
    
    security = await get_user_security(current_user.id)
    
    # Update PIN
    await db.user_security.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "pin_hash": hash_pin(request.pin),
            "pin_enabled": True,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {"message": "PIN setup successfully"}

@api_router.post("/security/verify-pin")
async def verify_pin_endpoint(
    request: VerifyPinRequest,
    current_user: User = Depends(get_current_user)
):
    """Verify user's PIN"""
    security = await get_user_security(current_user.id)
    
    if not security.pin_enabled or not security.pin_hash:
        raise HTTPException(status_code=400, detail="PIN not set up")
    
    if not verify_pin(request.pin, security.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    return {"message": "PIN verified successfully"}

@api_router.post("/security/send-sms-code")
async def send_sms_code(
    request: SendSMSCodeRequest,
    current_user: User = Depends(get_current_user)
):
    """Send SMS verification code"""
    # Generate 6-digit code
    code = generate_sms_code()
    
    # Store code with expiration (5 minutes)
    import time
    sms_codes[request.phone_number] = {
        "code": code,
        "expires_at": time.time() + 300,  # 5 minutes
        "user_id": current_user.id
    }
    
    # Send SMS
    message = f"Il tuo codice di verifica FarmyGo è: {code}. Valido per 5 minuti."
    success = await send_sms_notification(request.phone_number, message)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send SMS")
    
    return {"message": "SMS code sent successfully"}

@api_router.post("/security/verify-sms-code")
async def verify_sms_code(
    request: VerifySMSCodeRequest,
    current_user: User = Depends(get_current_user)
):
    """Verify SMS code"""
    import time
    
    if request.phone_number not in sms_codes:
        raise HTTPException(status_code=400, detail="No SMS code sent to this number")
    
    stored_code = sms_codes[request.phone_number]
    
    # Check expiration
    if time.time() > stored_code["expires_at"]:
        del sms_codes[request.phone_number]
        raise HTTPException(status_code=400, detail="SMS code expired")
    
    # Check code
    if stored_code["code"] != request.code:
        raise HTTPException(status_code=401, detail="Invalid SMS code")
    
    # Check user
    if stored_code["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="SMS code not for this user")
    
    # Clean up
    del sms_codes[request.phone_number]
    
    # Enable SMS security for user
    await db.user_security.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "sms_enabled": True,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {"message": "SMS code verified successfully"}

@api_router.post("/security/webauthn/generate-registration-options")
async def generate_webauthn_registration_options(
    current_user: User = Depends(get_current_user)
):
    """Generate WebAuthn registration options for Face ID/Touch ID"""
    if not WEBAUTHN_AVAILABLE:
        raise HTTPException(status_code=501, detail="WebAuthn not available")
    
    from webauthn import generate_registration_options
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        UserVerificationRequirement,
        AuthenticatorAttachment,
        ResidentKeyRequirement
    )
    
    options = generate_registration_options(
        rp_id="localhost",  # In production, use your domain
        rp_name="FarmyGo",
        user_id=current_user.id.encode(),
        user_name=current_user.username,
        user_display_name=current_user.username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            resident_key=ResidentKeyRequirement.DISCOURAGED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )
    
    # Store challenge for verification
    import time
    import base64
    challenge_key = f"webauthn_challenge_{current_user.id}"
    sms_codes[challenge_key] = {
        "challenge": base64.b64encode(options.challenge).decode('utf-8'),
        "expires_at": time.time() + 300,  # 5 minutes
        "user_id": current_user.id
    }
    
    # Convert options to JSON-serializable format
    return {
        "challenge": base64.b64encode(options.challenge).decode('utf-8'),
        "rp": {"id": options.rp.id, "name": options.rp.name},
        "user": {
            "id": base64.b64encode(options.user.id).decode('utf-8'),
            "name": options.user.name,
            "displayName": options.user.display_name
        },
        "pubKeyCredParams": [{"alg": param.alg, "type": param.type} for param in options.pub_key_cred_params],
        "timeout": options.timeout,
        "excludeCredentials": [],
        "authenticatorSelection": {
            "authenticatorAttachment": options.authenticator_selection.authenticator_attachment if options.authenticator_selection else None,
            "requireResidentKey": False,
            "userVerification": options.authenticator_selection.user_verification if options.authenticator_selection else "preferred"
        },
        "attestation": options.attestation
    }

@api_router.post("/security/webauthn/verify-registration")
async def verify_webauthn_registration(
    request: WebAuthnRegistrationRequest,
    current_user: User = Depends(get_current_user)
):
    """Verify WebAuthn registration and store credential"""
    if not WEBAUTHN_AVAILABLE:
        raise HTTPException(status_code=501, detail="WebAuthn not available")
    
    from webauthn import verify_registration_response
    from webauthn.helpers.structs import RegistrationCredential
    
    challenge_key = f"webauthn_challenge_{current_user.id}"
    if challenge_key not in sms_codes:
        raise HTTPException(status_code=400, detail="No registration challenge found")
    
    stored_challenge = sms_codes[challenge_key]
    
    try:
        # Convert request to proper format
        credential = RegistrationCredential.parse_raw(json.dumps(request.credential))
        
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=stored_challenge["challenge"].encode('latin-1'),
            expected_origin="http://localhost:3000",  # In production, use your domain
            expected_rp_id="localhost",
        )
        
        if verification.verified:
            # Store credential
            security = await get_user_security(current_user.id)
            new_credential = {
                "id": credential.id,
                "public_key": verification.credential_public_key.hex(),
                "sign_count": verification.sign_count,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.user_security.update_one(
                {"user_id": current_user.id},
                {"$push": {"webauthn_credentials": new_credential},
                 "$set": {
                     "face_id_enabled": True,
                     "updated_at": datetime.now(timezone.utc)
                 }}
            )
            
            # Clean up challenge
            del sms_codes[challenge_key]
            
            return {"message": "Face ID/Touch ID registered successfully"}
        else:
            raise HTTPException(status_code=400, detail="Registration verification failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@api_router.post("/security/webauthn/generate-authentication-options")
async def generate_webauthn_authentication_options(
    current_user: User = Depends(get_current_user)
):
    """Generate WebAuthn authentication options"""
    if not WEBAUTHN_AVAILABLE:
        raise HTTPException(status_code=501, detail="WebAuthn not available")
    
    from webauthn import generate_authentication_options
    from webauthn.helpers.structs import PublicKeyCredentialDescriptor, UserVerificationRequirement
    
    security = await get_user_security(current_user.id)
    
    if not security.webauthn_credentials:
        raise HTTPException(status_code=400, detail="No Face ID/Touch ID credentials registered")
    
    # Prepare allowed credentials
    allow_credentials = [
        PublicKeyCredentialDescriptor(id=cred["id"])
        for cred in security.webauthn_credentials
    ]
    
    options = generate_authentication_options(
        rp_id="localhost",
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    
    # Store challenge
    import time
    import base64
    challenge_key = f"webauthn_auth_challenge_{current_user.id}"
    sms_codes[challenge_key] = {
        "challenge": base64.b64encode(options.challenge).decode('utf-8'),
        "expires_at": time.time() + 300,
        "user_id": current_user.id
    }
    
    # Convert options to JSON-serializable format
    return {
        "challenge": base64.b64encode(options.challenge).decode('utf-8'),
        "timeout": options.timeout,
        "rpId": options.rp_id,
        "allowCredentials": [
            {
                "id": base64.b64encode(cred.id).decode('utf-8') if isinstance(cred.id, bytes) else cred.id,
                "type": cred.type,
                "transports": cred.transports if hasattr(cred, 'transports') else []
            }
            for cred in options.allow_credentials
        ],
        "userVerification": options.user_verification
    }

@api_router.post("/security/webauthn/verify-authentication")
async def verify_webauthn_authentication(
    request: WebAuthnAuthenticationRequest,
    current_user: User = Depends(get_current_user)
):
    """Verify WebAuthn authentication"""
    if not WEBAUTHN_AVAILABLE:
        raise HTTPException(status_code=501, detail="WebAuthn not available")
    
    from webauthn import verify_authentication_response
    from webauthn.helpers.structs import AuthenticationCredential
    
    challenge_key = f"webauthn_auth_challenge_{current_user.id}"
    if challenge_key not in sms_codes:
        raise HTTPException(status_code=400, detail="No authentication challenge found")
    
    stored_challenge = sms_codes[challenge_key]
    security = await get_user_security(current_user.id)
    
    # Find credential
    credential_id = request.credential.get("id")
    stored_credential = None
    for cred in security.webauthn_credentials:
        if cred["id"] == credential_id:
            stored_credential = cred
            break
    
    if not stored_credential:
        raise HTTPException(status_code=400, detail="Credential not found")
    
    try:
        credential = AuthenticationCredential.parse_raw(json.dumps(request.credential))
        
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=base64.b64decode(stored_challenge["challenge"]),
            expected_origin="http://localhost:3000",
            expected_rp_id="localhost",
            credential_public_key=bytes.fromhex(stored_credential["public_key"]),
            credential_current_sign_count=stored_credential["sign_count"],
        )
        
        if verification.verified:
            # Update sign count
            await db.user_security.update_one(
                {"user_id": current_user.id, "webauthn_credentials.id": credential_id},
                {"$set": {"webauthn_credentials.$.sign_count": verification.new_sign_count}}
            )
            
            # Clean up challenge
            del sms_codes[challenge_key]
            
            return {"message": "Face ID/Touch ID verified successfully"}
        else:
            raise HTTPException(status_code=401, detail="Authentication verification failed")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_super_admin()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()