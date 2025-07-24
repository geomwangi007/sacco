# SACCO Backend System - Claude Documentation

## Overview
This is a comprehensive **SACCO (Savings and Credit Cooperative Organization) Management System Backend** built with Django and Django REST Framework. The system provides complete financial services management for cooperative societies including member management, savings accounts, loans, transactions, and integrations with external financial services.

## Application Type
**Backend API Service** - A RESTful API backend that serves financial data and services to frontend applications, mobile apps, and third-party integrations.

## Technology Stack

### Core Framework
- **Django 4.2.20** - Web framework
- **Django REST Framework 3.15.2** - API framework
- **Python 3.10+** - Programming language

### Database & Caching
- **PostgreSQL** - Primary database (psycopg2-binary 2.9.5)
- **Redis** - Caching and message broker

### Async & Background Tasks
- **Celery 5.2.7** - Distributed task queue
- **Django Channels 4.0.0** - WebSocket and async support
- **Daphne** - ASGI server

### Additional Key Dependencies
- **django-cors-headers** - CORS handling
- **Pillow** - Image handling
- **Gunicorn** - WSGI server
- **python-dotenv** - Environment variables

## Project Structure

### Core Directory (`/core/`)
- `settings/` - Environment-specific settings (base, development, production, local)
- `urls.py` - Main URL routing
- `asgi.py` - ASGI application entry point
- `wsgi.py` - WSGI application entry point
- `celery.py` - Celery configuration

### Applications (`/apps/`)
The system follows a modular Django app structure:

#### Core Business Apps:
1. **authentication/** - User management, roles, permissions, JWT authentication
2. **members/** - Member profiles, KYC, next of kin, document management
3. **savings/** - Savings accounts, transactions, interest calculations
4. **loans/** - Loan applications, approvals, disbursements, repayments
5. **transactions/** - Financial transactions, fees, limits
6. **ledger/** - Double-entry bookkeeping and financial ledger

#### Support Apps:
7. **notifications/** - Email, SMS, push notifications with WebSocket support
8. **reporting/** - Financial reports, member reports, compliance reports
9. **risk_management/** - Fraud detection, compliance, risk assessment
10. **integrations/** - External service integrations (payment gateways, banks, mobile money)

### Shared Resources (`/shared/`)
- `mixins/` - Reusable model and serializer mixins
- `services/` - Common services (email, SMS, push notifications, ledger)
- `utils/` - Utility functions (date, number formatting, validators)
- `validators/` - Custom validation logic

### External Integrations (`/integrations/`)
- `bank/` - Banking system integrations
- `credit_bureau/` - Credit scoring and reporting
- `mobile_money/` - Mobile money payment integration
- `payment_gateway/` - Payment gateway abstractions
- `ussd/` - USSD service integration

### Configuration (`/config/`)
- `requirements/` - Environment-specific dependencies
- `gunicorn/` - Gunicorn server configuration
- `nginx/` - Nginx reverse proxy configuration

### Documentation (`/docs/`)
- `system_architecture.md` - System architecture overview
- `api.md` - API endpoints documentation
- `api_specs.md` - Detailed API specifications
- `deployment.md` - Deployment instructions

## Key Models & Data Structure

### User & Authentication
- **User** - Custom user model with email authentication, role-based permissions
- **Role** - User roles with granular permissions
- **Permission** - Fine-grained access control

### Member Management
- **Member** - Core member profile with KYC information
- **NextOfKin** - Emergency contacts and beneficiaries
- **MemberDocument** - Document management for verification

### Financial Core
- **SavingsAccount** - Member savings accounts with interest calculations
- **Loan** - Loan records with status tracking and repayment schedules
- **LoanApplication** - Loan application workflow
- **Transaction** - All financial transactions with audit trail

### Integration Points
- Payment gateways (mobile money, bank transfers)
- Credit bureau integration for loan scoring
- SMS/Email notification services
- Banking system interfaces

## Main Entry Points

### Django Management
- `manage.py` - Django command-line utility
- Settings module: `core.settings` (environment-dependent)

### API Endpoints (Base: `/api/v1/`)
- Authentication: `/api/v1/auth/`
- Members: `/api/v1/members/`
- Loans: `/api/v1/loans/`
- Integrations: `/api/v1/integrations/`
- Risk Management: `/api/v1/risk/`
- Ledger: `/api/v1/ledger/`
- Reporting: `/api/v1/reporting/`

## Key Features

### Financial Services
- Multi-type savings accounts (Regular, Fixed Deposit, Children, Group)
- Comprehensive loan management (application, approval, disbursement, repayment)
- Transaction processing with multiple payment methods
- Double-entry bookkeeping system
- Interest calculations and automated charges

### Risk & Compliance
- Fraud detection algorithms
- Credit scoring integration
- Compliance monitoring and reporting
- Transaction limits and controls

### Integration Capabilities
- Mobile money payment processing
- Bank integration for transfers
- SMS and email notifications
- Push notifications via WebSocket
- USSD service integration

### Security Features
- JWT-based authentication
- Role-based access control (RBAC)
- Account lockout after failed attempts
- Audit trails for all transactions
- IP tracking and logging

## Environment Configuration

### Database Configuration
- Primary: PostgreSQL with environment-based connection
- Timezone: `Africa/Kampala`
- Custom user model: `authentication.User`

### Async Services
- **Celery** with Redis broker for background tasks
- **Django Channels** with Redis for real-time features
- **ASGI** application for WebSocket support

### Key Environment Variables
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `CELERY_BROKER_URL`, `REDIS_URL`
- Various integration API keys and endpoints

## Development Workflow

### Local Development
1. Virtual environment with requirements from `config/requirements/development.txt`
2. SQLite fallback for local development
3. Django debug toolbar enabled
4. Hot reloading and development servers

### Testing
- Comprehensive test suites in each app's `tests/` directory
- Integration tests in `/tests/integration/`
- Models, views, and services are thoroughly tested

### Deployment
- Production settings in `core.settings.production`
- Gunicorn configuration for WSGI
- Nginx reverse proxy configuration
- Docker support with production Dockerfile

## Important Files to Know

### Configuration Files
- `/core/settings/base.py` - Core Django settings
- `/config/requirements/base.txt` - Core dependencies
- `/pyproject.toml` - Poetry project configuration

### Key Business Logic
- `/apps/loans/services/` - Loan processing services
- `/apps/savings/services/` - Savings account services
- `/apps/transactions/services/` - Transaction processing
- `/shared/services/ledger_service.py` - Double-entry bookkeeping

### Integration Services
- `/integrations/payment_gateway/` - Payment processing
- `/apps/risk_management/services/` - Risk assessment
- `/apps/notifications/services/` - Communication services

## Architecture Notes

### Design Patterns
- Service layer pattern for business logic
- Repository pattern for data access
- Factory pattern for payment gateway selection
- Observer pattern for transaction notifications

### Scalability Features
- Async task processing with Celery
- Redis caching layer
- Database indexing on critical queries
- Modular app structure for microservices migration

### Security Considerations
- All sensitive operations require authentication
- Role-based permissions throughout the system
- Transaction audit logging
- Rate limiting and request validation
- Secure file upload handling

This system represents a full-featured financial technology platform specifically designed for cooperative financial institutions, with emphasis on security, compliance, and scalability.