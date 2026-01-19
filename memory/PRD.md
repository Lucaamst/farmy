# FarmyGo - Delivery Management Platform

## Original Problem Statement
Build a comprehensive delivery management application for agricultural/food delivery companies with multiple roles (Super Admin, Company Admin, Courier). The system manages orders, deliveries, customers, and courier operations with features like digital signatures, 2FA authentication, PIN security, PDF reports, and real-time tracking.

## User Personas
1. **Super Admin**: Manages all companies and system-wide settings
2. **Company Admin**: Manages their company's couriers, orders, customers
3. **Courier**: Handles deliveries, signatures, route optimization

## Core Requirements
- Multi-tenant architecture with company isolation
- Role-based access control (RBAC)
- Order lifecycle management (pending → assigned → in_progress → delivered)
- Digital signature capture on delivery
- SMS notifications via Twilio (requires user API key)
- 2FA via Google Authenticator
- PIN-based quick access for couriers (web and mobile)
- PDF report generation (delivery confirmations, courier stats)
- Drag-and-drop delivery route optimization
- Multi-language support (Italian primary)

## Tech Stack
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Shadcn UI + react-beautiful-dnd
- **Mobile**: React Native / Expo (courier app)
- **Authentication**: JWT + 2FA (pyotp) + PIN

---

## What's Been Implemented (January 2025)

### Core Features ✅
- [x] User authentication (login/logout)
- [x] Role-based dashboards (Super Admin, Company Admin, Courier)
- [x] Company and user management
- [x] Order CRUD operations
- [x] Customer management
- [x] Courier assignment to orders

### Security Features ✅
- [x] 2FA via Google Authenticator
- [x] PIN security for couriers (web + mobile)
- [x] Change password functionality
- [x] **Auto-logout after 1 hour of inactivity** (NEW)
- [x] **Session lock with PIN re-authentication for couriers** (NEW)

### Delivery Features ✅
- [x] Digital signature capture
- [x] Delivery confirmation PDFs
- [x] Priority-based color coding
- [x] Drag-and-drop route reordering
- [x] Notes field on orders

### UI/UX Features ✅
- [x] Responsive design
- [x] Italian localization
- [x] Company branding (logo, name in header)
- [x] External document links (Privacy, Terms)
- [x] **Scrollable order creation dialog** (NEW)
- [x] **Courier full name display** (NEW)
- [x] **SMS status in customer history** (NEW)
- [x] **Unassigned Orders section with quick-assign** (NEW)

### Reporting ✅
- [x] Individual courier delivery stats PDF
- [x] All-couriers stats PDF
- [x] Company name on reports
- [x] Signature PDF download from history

---

## Latest Changes (January 19, 2025)

### Session 1 - 5 Feature Implementation
1. **Scrollable Order Dialog**: Added `max-h-[90vh] overflow-y-auto` to order creation dialog
2. **Courier Full Name**: `getCourierName()` now returns `full_name || username`
3. **SMS Status in History**: Shows "✓ SMS inviato" or "SMS non richiesto" in customer history
4. **Unassigned Orders Section**: Added prominent section in Company Admin overview with quick-assign dropdown
5. **Auto-logout with PIN**: 1-hour inactivity timeout, couriers with PIN see lock screen instead of full logout

### Bug Fixes
- Fixed quick-assign using wrong HTTP method (POST → PATCH)

---

## Pending Issues

### P1 - iOS PWA PIN Persistence
- **Issue**: Mobile app (PWA on iOS) may not consistently ask for PIN when closed/reopened
- **Status**: User verification pending
- **Debug steps**: Test on real iOS device, check AppState listener behavior

---

## Backlog / Future Tasks

### P1 - High Priority
- [ ] Map-based route optimization with real-time directions
- [ ] Backend refactoring (split server.py into modules)

### P2 - Medium Priority
- [ ] GDPR Cookie Banner (deferred until analytics added)
- [ ] Frontend refactoring (break App.js monolith into components)

### P3 - Low Priority
- [ ] Enhanced PDF reports with charts and trends
- [ ] Email notifications (alternative to SMS)
- [ ] Delivery time estimates

---

## Test Credentials
- **Super Admin**: superadmin / admin (2FA enabled)
- **Company Admin**: testadmin / test123 (no 2FA)
- **Courier**: testcourier / test123 (no PIN)

---

## Key Files Reference
- `/app/frontend/src/App.js` - Main frontend (6000+ lines, needs refactoring)
- `/app/backend/server.py` - Main backend API
- `/app/courier-app/App.js` - Mobile courier app

---

## Known Technical Debt
1. **App.js monolith**: Frontend App.js is 6000+ lines, prone to "white screen" errors
2. **server.py size**: Backend could be split into routers/modules
3. **No unit tests**: Consider adding pytest tests for backend

---

## Third-Party Integrations
- **Twilio SMS**: Requires user API key (not currently configured)
