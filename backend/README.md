# Backend - LottoAI API Server

This directory contains the FastAPI backend server that handles image processing, user authentication, prize checking, and automated lottery data scraping.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [File Structure](#file-structure)
- [Core Modules](#core-modules)
- [API Endpoints](#api-endpoints)
- [Authentication System](#authentication-system)
- [Database Integration](#database-integration)
- [Lottery Scraper](#lottery-scraper)
- [Data Flow](#data-flow)
- [Configuration](#configuration)
- [Development](#development)

---

## 🎯 Overview

The backend is built with **FastAPI**, a modern, high-performance Python web framework. It provides:

- **RESTful API endpoints** for frontend communication
- **AI/ML pipeline integration** (YOLO + EasyOCR)
- **User authentication** (JWT + OAuth)
- **Prize matching algorithm** with reverse number matching
- **Automated web scraping** for daily lottery updates
- **PostgreSQL integration** for data persistence

**Key Metrics:**
- Response time: < 3 seconds for image processing
- Concurrent requests: Handles async operations efficiently
- Uptime: 99.9% with proper deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│         fastapi_yoloocr_pipeline.py (Main App)      │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Lifespan Manager                            │   │
│  │  • Startup: Initialize scheduler             │   │
│  │  • Shutdown: Graceful cleanup                │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  CORS Middleware                             │   │ 
│  │  • Allow origins: localhost:5173, :3000      │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Router: auth_routes                         │   │
│  │  • /auth/signup, /auth/login, /auth/me       │   │
│  │  • /auth/google, /auth/google/callback       │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Endpoints: /upload/, /upload/debug/         │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
    ┌────────┐      ┌──────────┐      ┌──────────────┐
    │ auth.py│      │lottery_  │      │lottery_      │
    │        │      │checker.py│      │scraper.py    │
    │JWT +   │      │          │      │              │
    │Argon2  │      │Prize     │      │BeautifulSoup │
    └────────┘      │Algorithm │      │+ APScheduler │
                    └──────────┘      └──────────────┘
```

---

## 📁 File Structure

```
backend/
├── __init__.py                    # Makes backend a Python package
├── auth.py                        # Authentication utilities (JWT, passwords)
├── auth_routes.py                 # Authentication API endpoints
├── fastapi_yoloocr_pipeline.py   # Main FastAPI application
├── lottery_checker.py             # Prize matching algorithm
├── lottery_scheduler.py           # Daily scraper scheduler
├── lottery_scraper.py             # Web scraping logic
└── received_folder/               # Temporary image storage (debug mode)
```

---

## 🔧 Core Modules

### 1. `fastapi_yoloocr_pipeline.py` - Main Application

**Purpose:** Entry point for the FastAPI server. Orchestrates all components.

**Key Components:**

```python
# Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start lottery scheduler
    scheduler = start_scheduler()
    yield
    # Shutdown: Stop scheduler gracefully
    scheduler.shutdown()

# FastAPI instance with lifespan
app = FastAPI(lifespan=lifespan)
```

**Responsibilities:**
- Initialize FastAPI application
- Configure CORS middleware
- Register authentication routes
- Define upload endpoints
- Manage application lifecycle
- Handle database connections

**Key Functions:**

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `get_db_connection()` | Establish PostgreSQL connection | None | `psycopg2.connection` |
| `upload_form()` | Serve HTML upload form | None | `FileResponse` |
| `uploadfile()` | Process uploaded image | `file: UploadFile`, `debug: str`, `user_id: Optional[int]` | `dict` |

**Workflow:**
```
Request received → 
File validation → 
Bytes to NumPy (cv2.imdecode) → 
Call process_single_image() from pipeline.py → 
Call check_user_prizes() from lottery_checker.py → 
Save to database (if authenticated) → 
Return JSON response
```

---

### 2. `auth.py` - Authentication Utilities

**Purpose:** Provides secure password hashing and JWT token management.

**Security Features:**

**Password Hashing (Argon2):**
```python
ph = PasswordHasher(
    memory_cost=65536,    # 64 MB memory usage
    time_cost=3,          # 3 iterations
    parallelism=4         # 4 threads
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
```

**JWT Token Generation:**
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Token Validation:**
```python
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    # Extracts user_id from JWT token
    # Raises HTTPException if invalid/expired
```

**Configuration:**
- Algorithm: HS256
- Token expiration: 7 days (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Secret key: Loaded from `.env` (`JWT_SECRET_KEY`)

---

### 3. `auth_routes.py` - Authentication Endpoints

**Purpose:** Handles user registration, login, and OAuth flow.

**Data Models:**

```python
class SignUpRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    oauth_provider: Optional[str] = None
```

**Endpoints:**

#### `POST /auth/signup` - User Registration

**Process:**
1. Validate email format and uniqueness
2. Hash password using Argon2
3. Insert user into `users` table
4. Generate JWT token
5. Return token + user info

**Example Request:**
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "securePassword123"
}
```

**Example Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser"
  }
}
```

#### `POST /auth/login` - User Login

**Process:**
1. Query user by email
2. Verify password with Argon2
3. Generate JWT token
4. Return token

**Error Handling:**
- 404: User not found
- 401: Invalid password
- 500: Database error

#### `GET /auth/me` - Get Current User

**Headers Required:**
```
Authorization: Bearer <jwt_token>
```

**Returns:** User profile information

#### `GET /auth/google` - Initiate OAuth

**Process:**
1. Generate random state token (CSRF protection)
2. Store state with expiration (5 minutes)
3. Construct Google OAuth URL
4. Redirect user to Google login

#### `GET /auth/google/callback` - OAuth Callback

**Process:**
1. Validate state token
2. Exchange authorization code for access token
3. Fetch user info from Google
4. Create/update user in database
5. Generate JWT token
6. Redirect to frontend with token

**Error Handling:**
- Invalid state → 400 Bad Request
- OAuth error → 400 Bad Request
- Database error → 500 Internal Server Error

---

### 4. `lottery_checker.py` - Prize Matching Algorithm

**Purpose:** Implements the reverse number matching algorithm to check if a user's number wins any prizes.

**Core Algorithm:**

```python
def reverse_number_order(number: str) -> str:
    """Reverse number for right-to-left matching"""
    return number[::-1]
    # "123456" → "654321"

def finding_prize_section(extracted_reversed_list, reversed_userNum, total_num):
    """Find which prize tier matches"""
    target = reversed_userNum[:total_num]
    # For "517" reversed = "715"
    # Check 2 digits: "71"
    # Check 3 digits: "715"
    
    for key, value in extracted_reversed_list.items():
        if target in value:  # Exact match
            return [key]
    return []
```

**Prize Checking Flow:**

```
User number: "517"
                ↓
Reverse: "715"
                ↓
Check 2 digits: "71" → Prize 8? No
Check 3 digits: "715" → Prize 7? Yes! ✓
                ↓
Return: ["7"]
```

**Function:** `check_user_prizes(user_number: str, draw_date: Optional[str], region: Optional[str])`

**Parameters:**
- `user_number`: 6-digit lottery number
- `draw_date`: Optional specific date (defaults to latest)
- `region`: Optional region filter

**Returns:**
```python
{
    "matched_prizes": ["4", "7"],  # List of winning tiers
    "is_winner": True,
    "draw_info": {
        "draw_date": "2025-11-20",
        "region": "Đồng Nai"
    },
    "winning_numbers": {
        "prize_8": "53",
        "prize_7": "502",
        # ... all prize tiers
    }
}
```

**Database Integration:**

```python
def fetch_winning_numbers(draw_date, region):
    """Query latest draw from PostgreSQL"""
    query = """
        SELECT prize_8, prize_7, prize_6, ..., jp
        FROM winning_numbers
        WHERE draw_date = %s AND region = %s
        ORDER BY draw_date DESC
        LIMIT 1
    """
```

---

### 5. `lottery_scraper.py` - Web Scraping Module

**Purpose:** Automatically fetch daily lottery results from minhngoc.net.vn.

**Target Website:** https://www.minhngoc.net.vn/free/index.php

**HTML Structure Analysis:**

```html
<table class="bkqmiennam">
  <table class="rightcl">  <!-- Province 1: Đồng Nai -->
    <td class="tinh">Đồng Nai</td>
    <td class="giai8">53</td>
    <td class="giai7">502</td>
    <td class="giai6">8170 4154 9871</td>
    <!-- ... -->
  </table>
  <table class="rightcl">  <!-- Province 2: Cần Thơ -->
    <!-- ... -->
  </table>
  <table class="rightcl">  <!-- Province 3: Sóc Trăng -->
    <!-- ... -->
  </table>
</table>
```

**Scraping Process:**

```python
def scrape_lottery_results() -> List[Dict]:
    # 1. Fetch HTML
    response = requests.get("https://www.minhngoc.net.vn/free/index.php")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 2. Find main table
    main_table = soup.find('table', class_='bkqmiennam')
    
    # 3. Find all province tables inside
    province_tables = main_table.find_all('table', class_='rightcl')
    
    # 4. Extract data from each table
    for table in province_tables:
        province_data = extract_province_data(table, draw_date)
        results.append(province_data)
    
    return results
```

**Number Extraction:**

For prizes with multiple winners (Prize 6, 4, 3), numbers are concatenated without spaces:

```python
def extract_multiple_numbers(tbody, class_name):
    cell = tbody.find('td', class_=class_name)
    text = ''.join(cell.get_text(strip=True).split())  # "817041549871"
    
    # Determine digit length
    if class_name == 'giai6':
        digit_length = 4
    elif class_name in ['giai4', 'giai3']:
        digit_length = 5
    
    # Split into chunks
    numbers = []
    for i in range(0, len(text), digit_length):
        chunk = text[i:i+digit_length]
        if len(chunk) == digit_length:
            numbers.append(chunk)
    
    return numbers  # ['8170', '4154', '9871']
```

**Database Insertion:**

```python
def save_to_database(lottery_data: Dict) -> bool:
    # 1. Check for duplicates
    cursor.execute("""
        SELECT id FROM winning_numbers 
        WHERE draw_date = %s AND region = %s
    """, (lottery_data['draw_date'], lottery_data['province']))
    
    if cursor.fetchone():
        logger.warning("Draw already exists. Skipping.")
        return False
    
    # 2. Insert new draw
    cursor.execute("""
        INSERT INTO winning_numbers 
        (prize_8, prize_7, prize_6, prize_5, prize_4, prize_3, 
         prize_2, prize_1, jp_consolation, jp, draw_date, region)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        lottery_data['prize_8'],
        lottery_data['prize_7'],
        lottery_data['prize_6'],  # Array
        # ...
    ))
    
    conn.commit()
    return True
```

**JP Consolation Calculation:**

```python
# Jackpot: "300167"
# JP Consolation: Last 5 digits = "00167"

if lottery_data['jp'] and len(lottery_data['jp']) >= 5:
    lottery_data['jp_consolation'] = lottery_data['jp'][-5:]
```

---

### 6. `lottery_scheduler.py` - Task Scheduler

**Purpose:** Runs the lottery scraper daily at 4:45pm Vietnam time.

**Implementation:**

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

def start_scheduler():
    scheduler = BackgroundScheduler()
    vietnam_tz = timezone('Asia/Ho_Chi_Minh')
    
    # Schedule for 4:45pm daily
    scheduler.add_job(
        scrape_and_save,                    # Function to run
        trigger=CronTrigger(
            hour=16,                        # 4pm
            minute=45,                      # 45 minutes
            timezone=vietnam_tz
        ),
        id='lottery_scraper',
        name='Daily Lottery Scraper',
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler
```

**Integration with FastAPI:**

In `fastapi_yoloocr_pipeline.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler
    scheduler = start_scheduler()
    yield
    # Shutdown: Stop scheduler
    scheduler.shutdown()
```

**Behavior:**
- **If server starts before 4:45pm:** Waits until 4:45pm, then runs
- **If server starts after 4:45pm:** Waits until next day at 4:45pm
- **Runs in background:** Non-blocking, doesn't affect API performance
- **Logs output:** All scraping logs appear in console immediately

---

## 🔌 API Endpoints

### Authentication Routes (`/auth/*`)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/signup` | POST | No | Create new account |
| `/auth/login` | POST | No | Login with credentials |
| `/auth/me` | GET | JWT | Get current user info |
| `/auth/google` | GET | No | Initiate Google OAuth |
| `/auth/google/callback` | GET | No | Handle OAuth callback |

### Upload Routes

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/upload/` | GET | No | Serve HTML upload form |
| `/upload/` | POST | Optional | Upload & verify ticket |
| `/upload/debug/` | GET | No | Upload form with debug info |
| `/upload/debug/` | POST | Optional | Upload with full debug output |

### Debug Routes

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Root endpoint (redirect) |
| `/docs` | GET | No | Interactive API docs (Swagger) |
| `/redoc` | GET | No | Alternative API docs (ReDoc) |

---

## 🔐 Authentication System

### Flow Diagram

**Manual Signup/Login:**
```
User submits credentials
        ↓
Backend validates → Hash password (Argon2)
        ↓
Store in database
        ↓
Generate JWT token (HS256, 7-day expiration)
        ↓
Return token to frontend
        ↓
Frontend stores in localStorage
        ↓
Include in Authorization header for future requests
```

**Google OAuth:**
```
User clicks "Continue with Google"
        ↓
Redirect to Google login
        ↓
User authenticates with Google
        ↓
Google redirects back with auth code
        ↓
Backend exchanges code for user info
        ↓
Create/update user in database
        ↓
Generate JWT token
        ↓
Redirect to frontend with token
```

### Security Measures

1. **Password Storage:**
   - Argon2id algorithm (memory-hard)
   - 64 MB memory cost
   - 3 iterations
   - Salt generated automatically

2. **JWT Tokens:**
   - HS256 algorithm
   - 7-day expiration
   - Secret key from environment variable
   - Payload contains only user_id (minimal data)

3. **OAuth State Validation:**
   - Random state token generated per request
   - Stored with 5-minute expiration
   - Validated on callback to prevent CSRF

4. **CORS Protection:**
   - Whitelist of allowed origins
   - Credentials allowed only for trusted origins

---

## 🗄️ Database Integration

### Connection Management

```python
def get_db_connection():
    """
    Establish PostgreSQL connection using environment variables
    """
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
```

### Query Examples

**Insert User:**
```python
cursor.execute("""
    INSERT INTO users (email, username, password_hash)
    VALUES (%s, %s, %s)
    RETURNING id
""", (email, username, hashed_password))

user_id = cursor.fetchone()[0]
```

**Save User Number (Authenticated Upload):**
```python
cursor.execute("""
    INSERT INTO user_numbers (user_id, user_number)
    VALUES (%s, %s)
    ON CONFLICT (user_id, user_number) DO NOTHING
""", (user_id, extracted_number))
```

**Fetch Winning Numbers:**
```python
cursor.execute("""
    SELECT prize_8, prize_7, prize_6, prize_5, prize_4, 
           prize_3, prize_2, prize_1, jp_consolation, jp, 
           draw_date, region
    FROM winning_numbers
    WHERE draw_date = %s AND region = %s
    ORDER BY draw_date DESC
    LIMIT 1
""", (draw_date, region))
```

### Best Practices

- ✅ Always use parameterized queries (prevents SQL injection)
- ✅ Close connections in `finally` blocks
- ✅ Handle `psycopg2.Error` exceptions
- ✅ Use transactions for multi-step operations
- ✅ Index frequently queried columns

---

## 🕷️ Lottery Scraper

### Execution Schedule

**Cron Expression:** `0 45 16 * * *` (4:45pm daily, Vietnam time)

### Scraping Targets

|  Province |  Region  | Draw Days |
|-----------|----------|-----------|
| Đồng Nai  | Miền Nam |    Wed    |
| Cần Thơ   | Miền Nam |    Wed    |
| Sóc Trăng | Miền Nam |    Wed    |

*(Different provinces draw on different days)*

### Data Extraction

**Prize Tiers Scraped:**

|   Tier  | Digits | Multiple Winners? |   Storage   |
|---------|--------|-------------------|-------------|
| Prize 8 |    2   |         No        | VARCHAR(10) |
| Prize 7 |    3   |         No        | VARCHAR(10) |
| Prize 6 |    4   |        Yes (3)    |    TEXT[]   |
| Prize 5 |    4   |         No        | VARCHAR(10) |
| Prize 4 |    5   |        Yes (7)    |    TEXT[]   |
| Prize 3 |    5   |        Yes (2)    |    TEXT[]   |
| Prize 2 |    5   |         No        | VARCHAR(10) |
| Prize 1 |    5   |         No        | VARCHAR(10) |
| Jackpot |    6   |         No        | VARCHAR(10) |

### Error Handling

```python
# Network errors
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Network error: {e}")
    return []

# Parsing errors
try:
    province_data = extract_province_data(table, draw_date)
except Exception as e:
    logger.error(f"Parsing error: {e}")
    continue

# Database errors
try:
    save_to_database(lottery_data)
except psycopg2.Error as e:
    logger.error(f"Database error: {e}")
    conn.rollback()
```

---

## 🔄 Data Flow

### Upload & Verification Flow

```
1. User uploads image via frontend
        ↓
2. FastAPI receives multipart/form-data
        ↓
3. Extract file bytes
        ↓
4. Convert bytes → NumPy array (cv2.imdecode)
        ↓
5. Call process_single_image() from model_training/pipeline.py
   ├─ YOLO detects ticket ROI
   ├─ NumPy crops region
   └─ EasyOCR extracts number
        ↓
6. Validate extracted number (6 digits)
        ↓
7. Call check_user_prizes() from lottery_checker.py
   ├─ Query winning_numbers from database
   ├─ Reverse number matching algorithm
   └─ Determine winning tiers
        ↓
8. If user authenticated (JWT):
   └─ Save to user_numbers table
        ↓
9. Return JSON response with results
```

### Daily Scraper Flow

```
1. APScheduler triggers at 4:45pm Vietnam time
        ↓
2. lottery_scraper.scrape_lottery_results()
   ├─ Fetch HTML from minhngoc.net.vn
   ├─ Parse with BeautifulSoup
   ├─ Find main table (bkqmiennam)
   └─ Extract 3 province tables (rightcl)
        ↓
3. For each province:
   ├─ Extract province name
   ├─ Extract all prize tiers
   ├─ Calculate JP consolation
   └─ Return dictionary
        ↓
4. For each result:
   ├─ Check for duplicates (draw_date + region)
   └─ Insert into winning_numbers table
        ↓
5. Log results
```

---

## ⚙️ Configuration

### Environment Variables

Required in `.env`:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=lottoai_db
POSTGRES_USER=lottoai_user
POSTGRES_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your_secret_key

# OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### Configurable Constants

**In `auth.py`:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
```

**In `lottery_scheduler.py`:**
```python
CronTrigger(hour=16, minute=45, timezone='Asia/Ho_Chi_Minh')
```

**In `model_training/pipeline.py`:**
```python
MIN_CONFIDENCE = 0.30  # YOLO confidence threshold
```

---

## 🔨 Development

### Running Locally

```bash
# Activate virtual environment
source .venv312/bin/activate  # or .venv312\Scripts\activate on Windows

# Run with auto-reload
python -u -m uvicorn backend.fastapi_yoloocr_pipeline:app --reload

# Run with specific host/port
python -u -m uvicorn backend.fastapi_yoloocr_pipeline:app --host 0.0.0.0 --port 8000
```

### Testing Endpoints

**Using cURL:**
```bash
# Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Upload (guest)
curl -X POST http://localhost:8000/upload/ \
  -F "file=@ticket.jpg"

# Upload (authenticated)
curl -X POST http://localhost:8000/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@ticket.jpg"
```

**Using Swagger UI:**

Navigate to http://localhost:8000/docs for interactive API testing.

### Debugging

**Enable debug logging:**
```python
# In fastapi_yoloocr_pipeline.py
logging.basicConfig(level=logging.DEBUG)
```

**Check database:**
```bash
docker exec -it lottoai_db_postgres psql -U lottoai_user -d lottoai_db
```

**Manual scraper test:**
```bash
python backend/lottery_scraper.py
```
