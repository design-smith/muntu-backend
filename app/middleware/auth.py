from fastapi import Request, HTTPException
from ..utils.auth import get_current_user
from typing import List
from jose import jwt
from ..config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_auth(request: Request):
    # Get the full path including /api prefix
    path = request.url.path
    
    # Define public paths with /api prefix
    PUBLIC_PATHS = [
        "/api/auth/login",
        "/api/auth/signup",
        "/api/auth/refresh",
        "/api",
        "/api/docs",
        "/api/openapi.json"
    ]
    
    if path in PUBLIC_PATHS or request.method == "OPTIONS":
        return
        
    try:
        # Get token from query params or header
        token = request.query_params.get('token')
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            raise HTTPException(status_code=401, detail="No authentication token provided")

        try:
            # Print debug info
            print(f"Verifying token with secret: {settings.JWT_SECRET[:5]}...")
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            print("Token payload:", payload)
        except Exception as e:
            print(f"Token verification error: {str(e)}")  # Add error logging
            raise HTTPException(status_code=401, detail="Invalid authentication token")
            
        user = await get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        request.state.user = user
    except Exception as e:
        print(f"Auth middleware error: {str(e)}")  # Add error logging
        raise HTTPException(status_code=401, detail=str(e)) 