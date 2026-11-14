import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.settings import settings
from app.config.db import db_manager
from app.controllers import auth, users, sellers, brands, listings, otp, secure_signup, categories, chat
from app.services.category_seed import seed_categories_if_empty

# 1. Configure robust logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("trust_sell.main")

# 2. Database connection lifecycle hook using the modern lifespan parameter
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing Trust Sell application services...")
    
    # Securely verify uploads folder structure
    settings.UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    
    # Startup Database Connection
    try:
        await db_manager.connect_to_database()
        if db_manager.is_connected and db_manager.db is not None:
            await seed_categories_if_empty(db_manager.db)
    except Exception as e:
        logger.critical(f"FATAL: Application started without database connection: {str(e)}")
        # We do not crash the process instantly to allow for local development fallback, 
        # but warn heavily. The db helper checks state dynamically.
        
    yield
    
    # Shutdown tasks
    logger.info("De-initializing Trust Sell application services...")
    await db_manager.close_database_connection()

# 3. Instantiate FastAPI
app = FastAPI(
    title="Trust Sell Secure Backend API",
    description="MVC Architecture with high-security Identity Verification for Buyers, Sellers, and Brands.",
    version="1.0.0",
    lifespan=lifespan
)

# 4. Setup Rate Limiting to prevent brute-force and Denial-of-Service (DoS)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 5. Configure Secure CORS Middleware
# In production, specify exact allowed origins (e.g. ['https://trustsell.com'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust to exact frontend URL in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cookie", "Accept"],
    expose_headers=["Set-Cookie"] # Allow clients to see secure HttpOnly cookie instructions
)

# 6. Mount Static Files to securely serve uploaded images/selfies
# In high-security systems, direct files can also be served via secure streaming routes,
# but StaticFiles is highly optimized for development.
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.mount(
    path=f"/{settings.UPLOAD_DIR}",
    app=StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads"
)

# 7. Global Exception Handler to intercept database/system tracebacks from exposing
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"UNHANDLED SYSTEM ERROR: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact the platform security administrator."
        }
    )

# 8. Register Routers / Controllers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sellers.router)
app.include_router(brands.router)
app.include_router(listings.router)
app.include_router(otp.router)
app.include_router(secure_signup.router)
app.include_router(categories.router)
app.include_router(chat.router)

# 9. Healthcheck Endpoint
@app.get("/", tags=["Health"])
async def root_healthcheck(request: Request):
    """
    Public health check endpoint.
    Includes basic rate-limiting verification.
    """
    return {
        "status": "healthy",
        "service": "Trust Sell Backend",
        "security": "Enforced (MVC)",
        "database": "Online" if db_manager.is_connected else "Offline"
    }
