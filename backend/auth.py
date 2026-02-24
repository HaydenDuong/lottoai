# backend/auth.py
"""
Authentication Module
Handles JWT tokens, password hashing, and user authentication
"""

# ========== Imports and Environment Setup ==========
# HttpBearer = for reading tokens from the "Authorization: Bearer <token>" header
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# ========== Configuration ==========
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not yet set in .env, please double check or generate new with token_urlsafe(32)")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Production-ready Argon2 configuration
# Adjust based on the server resources:
# - memory_cost: Higher = more secure but slower (65536 = 64 MB)
# - timem_cost: Higher = more secure but slower (3 iterations = default)
# - parallelism: Number of threads (4 threads = default)
ph = PasswordHasher(
    memory_cost=65536,          # Adjust based on server RAM
    time_cost=3,                
    parallelism=4               # Adjust based on CPU cores
)

# Security scheme for JWT
security = HTTPBearer()

# ========== Password Functions ==========

def hash_password(password: str) -> str:
    """Hash a plain password"""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    
    except VerifyMismatchError:
        return False


# ========== JWT Token Functions ==========

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary to encode (usually {"sub": user_id})
        expires_delta: Optional expiration time
    
    Returns:
        Encoded JWT token string
    
    "sub" = subject (according to JWT docs)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dictionary
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ========== Dependency for Protected Routes ==========

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Dependency to get current authenticated user ID from JWT token
    
    Args:
        credentials: HTTP Bearer token from request header
    
    Returns:
        User ID (integer)
    
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return int(user_id)


# Optional: Allow both authenticated and anonymous users
async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[int]:
    """
    Dependency that returns user ID if authenticated, or None if anonymous
    Useful for endpoints that work for both logged-in and guest users
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except:
        return None