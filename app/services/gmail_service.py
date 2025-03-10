from typing import Optional, Dict, Any, List
import os
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from bson import ObjectId

from ..database import db
from ..config import settings

# OAuth configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.metadata'
]

class GmailService:
    def __init__(self):
        # Get environment variables from settings
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET
        redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

        # Debug print
        print("\nGmailService Initialization:")
        print(f"Settings loaded - Client ID: {'Present' if client_id else 'Missing'}")
        print(f"Redirect URI: {redirect_uri}")
        
        self.client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
                "javascript_origins": ["http://localhost:5173", "http://localhost:8000"]
            }
        }

    def create_oauth_flow(self, state: Optional[str] = None) -> Flow:
        """Create OAuth flow for Gmail authentication."""
        try:
            redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            print(f"Creating OAuth flow with redirect URI: {redirect_uri}")
            
            flow = Flow.from_client_config(
                self.client_config,
                scopes=SCOPES,
                state=state
            )
            
            # Explicitly set the redirect URI
            flow.redirect_uri = redirect_uri
            
            print("OAuth flow created successfully")
            return flow
            
        except Exception as e:
            print(f"Error creating OAuth flow: {str(e)}")
            raise

    def build_service(self, credentials: Credentials):
        """Build Gmail service from credentials."""
        return build('gmail', 'v1', credentials=credentials)

    async def refresh_token_if_needed(self, channel_id: str) -> bool:
        """Refresh token if expired or about to expire."""
        channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
        if not channel:
            return False

        try:
            # Check if token needs refresh (if expires in less than 5 minutes)
            expiry = datetime.fromisoformat(str(channel["metadata"]["token_expiry"]))
            if expiry - timedelta(minutes=5) <= datetime.utcnow():
                print(f"Token needs refresh. Expiry: {expiry}, Current: {datetime.utcnow()}")
                credentials = Credentials(
                    token=channel["metadata"]["access_token"],
                    refresh_token=channel["metadata"]["refresh_token"],
                    token_uri=self.client_config["web"]["token_uri"],
                    client_id=self.client_config["web"]["client_id"],
                    client_secret=self.client_config["web"]["client_secret"],
                    scopes=SCOPES
                )

                if credentials.expired:
                    print("Refreshing expired credentials")
                    credentials.refresh(Request())

                    # Update tokens in database
                    await db.channels.update_one(
                        {"_id": ObjectId(channel_id)},
                        {"$set": {
                            "metadata.access_token": credentials.token,
                            "metadata.refresh_token": credentials.refresh_token,
                            "metadata.token_expiry": credentials.expiry.isoformat()
                        }}
                    )
                    print(f"Tokens updated. New expiry: {credentials.expiry}")

            return True

        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            # Token refresh failed
            await db.channels.update_one(
                {"_id": ObjectId(channel_id)},
                {"$set": {"status": "inactive"}}
            )
            return False

    async def setup_watch(self, channel_id: str) -> Dict[str, Any]:
        """Set up Gmail push notifications for new messages."""
        print(f"Starting watch setup for channel: {channel_id}")
        channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
        if not channel:
            raise Exception("Channel not found")

        credentials = Credentials(
            token=channel["metadata"]["access_token"],
            refresh_token=channel["metadata"]["refresh_token"],
            token_uri=self.client_config["web"]["token_uri"],
            client_id=self.client_config["web"]["client_id"],
            client_secret=self.client_config["web"]["client_secret"],
            scopes=SCOPES
        )

        service = build('gmail', 'v1', credentials=credentials)
        
        try:
            # Use a single topic for all Gmail notifications
            topic_name = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/topics/gmail-notifications"
            print(f"Using Pub/Sub topic: {topic_name}")
            
            request = {
                'labelIds': ['INBOX'],
                'topicName': topic_name,
                'labelFilterAction': 'include',
                'userId': 'me'
            }
            print(f"Watch request payload: {request}")
            
            response = service.users().watch(userId='me', body=request).execute()
            print(f"Watch response: {response}")
            
            if response:
                update_data = {
                    "metadata.watch_active": True,
                    "metadata.watch_expiry": datetime.fromtimestamp(int(response.get('expiration', 0)) / 1000),
                    "metadata.history_id": response.get('historyId')
                }
                print(f"Updating channel with watch data: {update_data}")
                await db.channels.update_one(
                    {"_id": ObjectId(channel_id)},
                    {"$set": update_data}
                )
            
            return response
            
        except Exception as e:
            print(f"Error setting up Gmail watch: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
            raise

# Create a global instance
gmail_service = GmailService() 