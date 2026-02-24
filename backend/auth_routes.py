# backend/auth_routes.py
"""
Authentication Routes
Handles user registration, login, and user info endpoints
"""
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi.responses import RedirectResponse
import secrets
import requests as http_requests                                
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import psycopg2
from backend.auth import hash_password, verify_password, create_access_token, get_current_user_id
import os
from dotenv import load_dotenv


load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ========== Request/Response Models ==========

class SignUpRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    oauth_provider: Optional[str] = None        # Allow None


# ========== Database Helper ==========

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT")),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        return conn
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail="Database unavailable")


# ========== Authentication Endpoints for Manual Sign-Up, Sign-In & Upload ==========

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignUpRequest):
    """
    Register a new user
    
    Returns JWT token on success
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password and insert user
        hashed_password = hash_password(data.password)
        
        cursor.execute(
            """
            INSERT INTO users (email, username, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (data.email, data.username, hashed_password)
        )
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        print(f"✅ New user registered: {data.username} (ID: {user_id})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Signup error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Login with email and password
    
    Returns JWT token on success
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find user by email
        cursor.execute(
            """
            SELECT id, password_hash, is_active
            FROM users
            WHERE email = %s
            """,
            (data.email,)
        )
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_id, password_hash, is_active = user
        
        # Check if account is active
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Verify password
        if not verify_password(data.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        print(f"✅ User logged in: ID {user_id}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int = Depends(get_current_user_id)):
    """
    Get current authenticated user's information
    
    Requires valid JWT token in Authorization header
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, email, username, oauth_provider
            FROM users
            WHERE id = %s AND is_active = TRUE
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user[0],
            "email": user[1],
            "username": user[2],
            "oauth_provider": user[3]
        }
        
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"❌ Get user error: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch user")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ========== Google OAuth Endpoints ==========

# Store temporary state tokens
# For production-ready level, Docker-Redis container will be utilized
# For now, a dictionary structure will be used instead
oauth_states = {}

@router.get("/google")
async def google_login():
    """
    Initiate Google OAuth login
    Redirecs user to Google's login page
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    # DEBUG
    # print(f"DEBUG Client ID: {client_id}")
    # print(f"DEBUG Redirect URI: {redirect_uri}")
    
    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )
    
    # Generate random state token for CSRF protection
    # This is per OAuth login: 
    # The web app will generate this token & send it to OAuth provider in https://github.com/login/oauth/authorize?state=<state>
    # OAuth will redirects back to client /callback?code=xxxx&state=<same_state>
    # Backend server will compare the received "state" from OAuth provider with initial token to prevent CSRF attack
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True
    
    # Build Google OAuth URL
    google_oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"state={state}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    # print(f"DEBUG: Redirecting to: {google_oauth_url}")
    
    return RedirectResponse(url=google_oauth_url)

@router.get("/google/callback")
async def google_callback(code: str, state: str):
    """
    Handle Google OAuth callback
    Exchange authorization code for user info, create / login user
    """
    # Verify state token (CSRF protection)
    if state not in oauth_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid state token"
        )
    
    # Delete after verification to prevent unwanted leverage
    del oauth_states[state]
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    conn = None
    cursor = None

    try:
        # Exchange authorization code for access token
        token_response = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        )
        
        if not token_response.ok:
            raise HTTPException(status_code=400, detail="Failed to get access token from Google")
        
        token_data = token_response.json()
        id_token_jwt = token_data.get('id_token')
        
        if not id_token_jwt:
            raise HTTPException(status_code=400, detail="No ID token received from Google")
        
        # Verify and decode ID token
        idinfo = id_token.verify_oauth2_token(
            id_token_jwt,
            google_requests.Request(),
            client_id
        )
        
        # Extract user info from token
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        
        # Check if user exists with this Google ID
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id FROM users 
            WHERE oauth_provider = 'google' AND oauth_id = %s
            """,
            (google_id,)
        )
        
        user = cursor.fetchone()
        
        if user:
            # User exists, log them in
            user_id = user[0]
            print(f"✅ Existing Google user logged in: ID {user_id}")
            
        else:
            # Check if email already exists (manual signup)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Email exists with manual signup, link Google account
                cursor.execute(
                    """
                    UPDATE users 
                    SET oauth_provider = 'google', oauth_id = %s
                    WHERE email = %s
                    """,
                    (google_id, email)
                )
                user_id = existing_user[0]
                print(f"✅ Linked Google account to existing user: ID {user_id}")
                
            else:
                # Create new user
                # Generate unique username from email
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                
                while True:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    if not cursor.fetchone():
                        break
                    username = f"{base_username}{counter}"
                    counter += 1
                
                cursor.execute(
                    """
                    INSERT INTO users (email, username, oauth_provider, oauth_id, password_hash)
                    VALUES (%s, %s, 'google', %s, NULL)
                    RETURNING id
                    """,
                    (email, username, google_id)
                )
                
                user_id = cursor.fetchone()[0]
                print(f"✅ New Google user created: {username} (ID: {user_id})")
        
        conn.commit()
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:5173/?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Google OAuth error: {e}")
        # Redirect to frontend with error
        frontend_url = f"http://localhost:5173/?error=oauth_failed"
        return RedirectResponse(url=frontend_url)
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()