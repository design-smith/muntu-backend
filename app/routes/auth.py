from fastapi import APIRouter, Depends, HTTPException, status, Body, Form
from fastapi.security import OAuth2PasswordRequestForm
from ..models.user import UserCreate, User, UserResponse
from ..utils.auth import get_password_hash, verify_password, create_access_token, get_current_user
from ..database import db
from datetime import datetime, timedelta, timezone
from typing import Dict
from ..models.auth import LoginData, SignupData
from pydantic import ValidationError

router = APIRouter()

@router.post("/signup")
async def signup(user_data: UserCreate):
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document with all required fields
        user = {
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "organizations": [],
            "preferences": {
                "theme": "light",
                "language": "en",
                "notifications": {
                    "email": True,
                    "push": True,
                    "desktop": True
                }
            }
        }
        
        # Insert into database
        result = await db.users.insert_one(user)
        user_id = str(result.inserted_id)
        
        # Create access token
        access_token = create_access_token(user_id)
        
        # Return response
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }
        }
    except Exception as e:
        print(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(login_data: LoginData):
    try:
        # Find user by email
        user = await db.users.find_one({"email": login_data.email})
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Check if hashed_password exists
        if "hashed_password" not in user:
            raise HTTPException(
                status_code=500,
                detail="User account is corrupted. Please contact support."
            )

        # Verify password using hashed_password field
        if not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Create access token
        access_token = create_access_token(str(user["_id"]))

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", "")
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return User(**current_user)

@router.post("/logout")
async def logout():
    # For JWT, we don't need to do anything server-side
    # The client should remove the token
    return {"message": "Successfully logged out"} 