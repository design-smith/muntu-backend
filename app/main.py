from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .routes import auth, users, organizations, assistants, conversations, customers, catalog, team, products, contacts, integrations
from .middleware.auth import verify_auth
from .config import settings
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent / '.env'
print(f"Loading environment variables from: {env_path}")

# Load environment variables
load_dotenv(dotenv_path=env_path)

# Debug print environment variables
print("Environment variables loaded:")
print(f"GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID', 'Not found')}")
print(f"GOOGLE_OAUTH_REDIRECT_URI: {os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'Not found')}")

# Verify required environment variables
required_vars = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_OAUTH_REDIRECT_URI"
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# OAuth2 scheme for Swagger UI - update tokenUrl to match the actual endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",  # Updated to match the actual endpoint
    scheme_name="OAuth2",
    description="JWT Bearer token authentication"
)

app = FastAPI(
    title="Muntu API",
    description="Muntu AI Customer Service Platform API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,  # Changed to True for auth
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler for all exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global error handler: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for OPTIONS requests
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    # Skip auth for auth routes and docs
    if request.url.path.startswith("/api/auth/") or request.url.path in ["/docs", "/openapi.json"]:
        response = await call_next(request)
        return response
    
    try:
        await verify_auth(request)
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"Auth middleware error: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"detail": str(e)}
        )

# Include routers with auth dependencies
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    organizations.router,
    prefix="/api/organizations",
    tags=["Organizations"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    assistants.router,
    prefix="/api/assistants",
    tags=["Assistants"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    conversations.router,
    prefix="/api/conversations",
    tags=["Conversations"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    customers.router,
    prefix="/api/customers",
    tags=["Customers"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    catalog.router,
    prefix="/api/catalog",
    tags=["Catalog"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    team.router,
    prefix="/api/team",
    tags=["Team"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    products.router,
    prefix="/api/products",
    tags=["Products"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    contacts.router,
    prefix="/api/contacts",
    tags=["Contacts"],
    dependencies=[Depends(oauth2_scheme)]
)

app.include_router(
    integrations.router,
    prefix="/api/integrations",
    tags=["Integrations"],
    dependencies=[Depends(oauth2_scheme)]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Muntu API"} 