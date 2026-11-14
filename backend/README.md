# Trust Sell Secure Backend API

Welcome to the backend engine of **Trust Sell**, a security-first e-commerce trust platform designed on a solid **MVC (Model-View-Controller)** architecture using **Python FastAPI** and **MongoDB Atlas** (integrated asynchronously via the `motor` driver).

---

## 🔒 High-Security Infrastructure & Core Pillars

Unlike generic open e-commerce applications, **Trust Sell** is designed to guarantee high trust and security:

1. **Mandatory Identity Verification**: Both Buyers and Sellers/Brands are required to provide verifiable government identities upon signup.
2. **Camera Selfie Uploads (Anti-Fraud)**: Integrated selfie/live-photo capture verification for all roles at registration to prevent bot creation, identity theft, and fake seller shops.
3. **Admin Onboarding Guard**: Sellers and Brands are set to `pending` by default and **cannot list products or execute actions** until an authorized Administrator reviews and approves their national ID (CNIC) and trademark registrations.
4. **JWT Session Protection**: Authentication tokens are signed using high-entropy `HS256` keys and can be saved in **HttpOnly, Secure, SameSite=Lax cookies** to completely prevent Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) attacks.
5. **Secure Upload Sanitization**: Uploaded files (selfies, licenses, trademark certificates) are:
   - Validated against a strict whitelist of MIME types (`image/jpeg`, `image/png`, `application/pdf`).
   - Inspected for strict maximum file sizes (3MB for selfies, 5MB for documents) to block DoS storage attacks.
   - **Renamed to random UUIDs** upon saving to completely neutralize path traversal (`../../etc/passwd`) or arbitrary code execution (uploading `.py` or `.php`) exploits.
6. **API Rate Limiting**: Key endpoints are guarded using a rate-limiting middleware (`slowapi`) to block brute-force password guessing and script-based request flooding.
7. **Production Error Masking**: Handlers intercept system tracebacks globally, rendering uniform JSON errors instead of exposing details about server variables.

---

## 📁 MVC Architecture Directory Layout

```
backend/
├── app/
│   ├── main.py                 # API bootstrap, CORS, rate limits, global error handling
│   ├── config/
│   │   ├── db.py               # Async MongoDB connection manager (Motor)
│   │   └── settings.py         # Config loader reading from secure .env variables
│   ├── controllers/            # CONTROLLERS (handles HTTP requests and router routing)
│   │   ├── auth.py             # Secure signup (Buyer, Seller, Brand) and secure JWT Login
│   │   ├── users.py            # User profile management and selfie/camera updating
│   │   ├── sellers.py          # Seller onboarding audits, status checking, and admin verification
│   │   └── brands.py           # Brand trademark profile management and admin certification audits
│   ├── models/                 # MODELS (MongoDB document schemas and DB dictionaries)
│   │   ├── user.py             # User schema with selfie references
│   │   ├── seller.py           # Seller schema with category, shop, CNIC, and documents
│   │   └── brand.py            # Brand schema with trademark number and certificate
│   ├── schemas/                # VIEWS (Pydantic serialization, input validation & data filters)
│   │   ├── auth.py             # Login credentials and access tokens
│   │   ├── user.py             # Safe, filtered public/private user profile serializations
│   │   ├── seller.py           # Populated seller representation
│   │   └── brand.py            # Populated brand representative representation
│   └── services/               # Cryptography and Verification utilities
│       ├── security.py         # Cryptographic bcrypt hashing, JWT validation, and RBAC policies
│       └── verification.py     # Upload checkers (MIME, sizes, directory sanitization)
├── .env                        # Local and production environment credentials
├── requirements.txt            # System dependencies
└── README.md                   # Setup and execution guide
```

---

## 🚀 Setting Up the Backend

### 1. Prerequisites
- Python 3.10 or higher
- MongoDB Atlas account (or a running local instance of MongoDB)

### 2. Installation
Navigate to the `backend` folder and set up a Python virtual environment:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Connect MongoDB Atlas
Create or open the `.env` file in the root `backend` directory.

When you create your MongoDB Atlas Database:
1. Go to **Atlas Dashboard -> Database -> Connect**.
2. Select **Drivers** (Python).
3. Copy the Connection String. It looks like:
   `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`
4. Replace the default local URL in the `.env` file:
   ```env
   MONGODB_URL=mongodb+srv://your_username:your_password@cluster0.mongodb.net/?retryWrites=true&w=majority
   DATABASE_NAME=trust_sell
   ```

### 4. Run Server
Launch the backend server using `uvicorn`:
```powershell
uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

---

## 📖 API Documentation & Sandbox
Once the server is running, FastAPI automatically compiles and serves interactive Swagger documentation:
- **Interactive Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative Schema Explorer**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛡️ Identity Verification API Walkthrough

### 1. Onboarding a Buyer
- **Endpoint**: `POST /auth/signup/buyer` (Multipart Form-Data)
- **Required Fields**:
  - `name`: Text
  - `email`: Text (validated syntax)
  - `phone`: Text (verified length/format)
  - `password`: Text (minimum 8 characters)
  - `selfie`: File Upload (`.jpg`, `.jpeg`, `.png` only)

### 2. Onboarding a Seller (Starts Pending)
- **Endpoint**: `POST /auth/signup/seller` (Multipart Form-Data)
- **Required Fields**:
  - `name`, `email`, `phone`, `password`
  - `shop_name`: Unique shop name
  - `seller_category`: One of `Individual`, `Retailer`, `Wholesaler`, `Manufacturer`
  - `cnic_number`: Format `XXXXX-XXXXXXX-X`
  - `selfie`: File Upload (Live Face Picture)
  - `document`: File Upload (CNIC Front/Back or Trade License)

### 3. Onboarding a Brand (Starts Pending)
- **Endpoint**: `POST /auth/signup/brand` (Multipart Form-Data)
- **Required Fields**:
  - `name`, `email`, `phone`, `password`
  - `brand_name`: Unique brand registration name
  - `brand_category`: Text category
  - `trademark_number`: Registry ID
  - `selfie`: File Upload (Brand Representative Selfie)
  - `certificate`: File Upload (Trademark Registration Certificate)

### 4. Admin Auditing and Approvals
- **Retrieve Pending Accounts**: `GET /sellers/pending` and `GET /brands/pending` (Admin credentials required).
- **Audit Verification Status**:
  - `POST /sellers/{seller_id}/verify` (Parameters: `approve` [True/False], `rejection_reason` [optional])
  - `POST /brands/{brand_id}/verify` (Parameters: `approve` [True/False], `rejection_reason` [optional])
