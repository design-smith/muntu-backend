from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Optional
from ..services.gmail_service import gmail_service
from ..utils.auth import get_current_user
from ..database import db
from datetime import datetime
import os

router = APIRouter()

@router.get("/gmail/connect")
async def gmail_connect(current_user: dict = Depends(get_current_user)):
    """
    Initiate Gmail OAuth flow
    """
    try:
        print(f"Starting Gmail OAuth flow for user: {current_user['email']}")
        
        # Verify environment variables
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
        
        print(f"Using client_id: {client_id[:10]}...")
        print(f"Using redirect_uri: {redirect_uri}")
        
        if not client_id or not redirect_uri:
            raise HTTPException(
                status_code=500,
                detail="Missing required environment variables"
            )
        
        # Create OAuth flow
        flow = gmail_service.create_oauth_flow()
        
        # Get authorization URL with explicit parameters
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            redirect_uri=redirect_uri
        )
        
        print(f"Generated auth URL: {auth_url}")
        return {"auth_url": auth_url}
        
    except Exception as e:
        print(f"Error in gmail_connect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/oauth/callback/gmail")
async def gmail_callback(
    code: str,
    state: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Handle Gmail OAuth callback
    """
    try:
        print(f"Received callback with code: {code[:10]}...")  # Debug log
        
        # Create flow and fetch token
        flow = gmail_service.create_oauth_flow(state=state)
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user email using Gmail API
        service = gmail_service.build_service(credentials)
        profile = service.users().getProfile(userId='me').execute()
        email = profile['emailAddress']

        print(f"Got email profile for: {email}")  # Debug log

        # Create or update channel
        channel_data = {
            "businessId": current_user["organization_id"],
            "type": "email",
            "identifier": email,
            "status": "active",
            "metadata": {
                "provider": "gmail",
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expiry": credentials.expiry.isoformat(),
                "watch_active": False
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Check if channel already exists
        existing_channel = await db.channels.find_one({
            "businessId": current_user["organization_id"],
            "type": "email",
            "identifier": email
        })

        if existing_channel:
            # Update existing channel
            await db.channels.update_one(
                {"_id": existing_channel["_id"]},
                {"$set": {
                    "status": "active",
                    "metadata": channel_data["metadata"],
                    "updated_at": channel_data["updated_at"]
                }}
            )
            channel_id = str(existing_channel["_id"])
            print(f"Updated existing channel: {channel_id}")  # Debug log
        else:
            # Create new channel
            result = await db.channels.insert_one(channel_data)
            channel_id = str(result.inserted_id)
            print(f"Created new channel: {channel_id}")  # Debug log

        # Set up Gmail watch
        await gmail_service.setup_watch(channel_id)

        return {
            "success": True,
            "channel_id": channel_id,
            "email": email
        }

    except Exception as e:
        print(f"Error in gmail_callback: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/gmail/disconnect/{channel_id}")
async def gmail_disconnect(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect Gmail integration
    """
    try:
        # Get channel
        channel = await db.channels.find_one({"_id": channel_id})
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        # Verify ownership
        if channel["businessId"] != current_user["organization_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Update channel status
        await db.channels.update_one(
            {"_id": channel_id},
            {
                "$set": {
                    "status": "inactive",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 