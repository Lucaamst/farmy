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
    status: str = "pending"  # pending, assigned, in_progress, delivered
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None
    sms_sent: bool = False

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

class CreateCourierRequest(BaseModel):
    username: str
    password: str

class UpdateCourierRequest(BaseModel):
    username: str
    password: Optional[str] = None

class CreateOrderRequest(BaseModel):
    customer_name: str
    delivery_address: str
    phone_number: str
    reference_number: Optional[str] = None

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

async def send_sms_notification(phone_number: str, message: str):
    """Mock SMS service - in production, integrate with Twilio"""
    print(f"SMS SENT to {phone_number}: {message}")
    # Store SMS log
    sms_log = {
        "id": str(uuid.uuid4()),
        "phone_number": phone_number,
        "message": message,
        "sent_at": datetime.now(timezone.utc),
        "status": "sent"
    }
    await db.sms_logs.insert_one(sms_log)
    return True

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
    order = Order(
        customer_name=request.customer_name,
        delivery_address=request.delivery_address,
        phone_number=request.phone_number,
        reference_number=request.reference_number,
        company_id=current_user.company_id
    )
    await db.orders.insert_one(order.dict())
    
    return {"message": "Order created successfully", "order": order}

@api_router.get("/orders", response_model=List[Order])
async def get_orders(
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    orders = await db.orders.find({
        "company_id": current_user.company_id
    }).to_list(1000)
    
    return [Order(**order) for order in orders]

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

@api_router.patch("/orders/assign")
async def assign_order(
    request: AssignOrderRequest,
    current_user: User = Depends(require_role([UserRole.COMPANY_ADMIN]))
):
    # Verify courier belongs to same company
    courier = await db.users.find_one({
        "id": request.courier_id,
        "company_id": current_user.company_id,
        "role": UserRole.COURIER,
        "is_active": True
    })
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found or inactive")
    
    # Update order
    result = await db.orders.update_one(
        {"id": request.order_id, "company_id": current_user.company_id},
        {"$set": {
            "courier_id": request.courier_id,
            "status": "assigned"
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order assigned successfully"}

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
    
    # Send SMS notification
    message = f"Hello {order['customer_name']}, your package has been delivered to {order['delivery_address']}. Thank you!"
    await send_sms_notification(order["phone_number"], message)
    
    return {"message": "Delivery marked as completed and customer notified"}

@api_router.get("/sms-logs")
async def get_sms_logs(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]))
):
    """Get SMS logs for verification"""
    sms_logs = await db.sms_logs.find().sort("sent_at", -1).to_list(50)
    return sms_logs

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