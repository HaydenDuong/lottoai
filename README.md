# LottoAI - AI-Powered Lottery Ticket Verification System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.2.0-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)

LottoAI is a comprehensive full-stack application that leverages computer vision and OCR technology to automatically verify lottery tickets against winning numbers. The system features daily automated updates of lottery results, user authentication, and intelligent prize matching algorithms.

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Core Functionality
- **AI-Powered Ticket Recognition**: Uses YOLOv11n for lottery ticket detection and EasyOCR for number extraction
- **Automated Prize Checking**: Matches user numbers against 9 prize tiers (Prize 8 through Jackpot)
- **Daily Automated Updates**: Web scraper fetches latest lottery results daily at 4:45pm Vietnam time
- **Multi-Province Support**: Currently supports 3 provinces in Miền Nam region (Vietnam Southern Lottery)

### User Management
- **Dual Authentication**: Manual signup with email/password (Argon2 hashing) or Google OAuth
- **Guest Mode**: Upload and check tickets without creating an account
- **Secure Sessions**: JWT tokens with 7-day expiration
- **User History**: Authenticated users can track uploaded numbers (future enhancement)

### Technical Features
- **RESTful API**: FastAPI backend with automatic Swagger documentation
- **Real-time Processing**: < 3 second response time for ticket verification
- **Containerized Database**: PostgreSQL running in Docker with persistent storage
- **Responsive UI**: Modern React frontend with Framer Motion animations

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI framework |
| Vite | 7.2.2 | Build tool & dev server |
| Styled Components | 6.1.19 | CSS-in-JS styling |
| Framer Motion | 12.23.24 | Animations |
| Axios | 1.13.2 | HTTP client |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Async web framework |
| Uvicorn | ASGI server |
| Psycopg2 | PostgreSQL driver |
| Python-Jose | JWT handling |
| Argon2-cffi | Password hashing |

### AI/ML
| Technology | Purpose |
|------------|---------|
| YOLOv11n | Object detection |
| EasyOCR | Optical character recognition |
| OpenCV | Image format conversion |
| NumPy | Array operations |

### Database & Infrastructure
| Technology | Purpose |
|------------|---------|
| PostgreSQL 15 | Relational database |
| Docker & Docker Compose | Containerization |
| APScheduler | Task scheduling |
| BeautifulSoup4 | Web scraping |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 CLIENT (Web Browser)                    │
│              React SPA + Styled Components              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS (Port 5173)
                     ↓
┌─────────────────────────────────────────────────────────┐
│              BACKEND API SERVER (FastAPI)               │
│                    Port 8000                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Endpoints:                                      │   │
│  │  • /upload/ - Image processing                   │   │
│  │  • /auth/signup - User registration              │   │
│  │  • /auth/login - Authentication                  │   │
│  │  • /auth/google - OAuth flow                     │   │
│  └──────────────────────────────────────────────────┘   │
└──┬───────────────┬─────────────────┬────────────────────┘
   │               │                 │
   ↓               ↓                 ↓
┌─────────┐  ┌──────────┐   ┌──────────────────┐
│  AI/ML  │  │PostgreSQL│   │  Web Scraper     │
│Pipeline │  │ Database │   │  (Scheduled)     │
│         │  │          │   │                  │
│ YOLO ─► │  │ • users  │   │ • BeautifulSoup  │
│ EasyOCR │  │ • numbers│   │ • APScheduler    │
│ OpenCV  │  │ • prizes │   │ • Daily @4:45pm  │
└─────────┘  └──────────┘   └──────────────────┘
```

### Data Flow

**Upload & Verification Flow:**
```
User uploads image → FastAPI receives file → 
OpenCV decodes bytes → YOLOv11n detects ticket ROI → 
NumPy crops region → EasyOCR extracts numbers → 
Regex cleans digits → Query database → 
Algorithm checks prizes → Return results
```

**Daily Scraper Flow:**
```
4:45pm Vietnam time → APScheduler triggers → 
Scraper fetches minhngoc.net.vn → Parse HTML → 
Extract 3 provinces' results → Store in PostgreSQL → 
Available for next prize checks
```

---

## 📁 Project Structure

```
LottoAI/
├── backend/                    # Backend API server
│   ├── auth.py                # JWT & password utilities
│   ├── auth_routes.py         # Authentication endpoints
│   ├── fastapi_yoloocr_pipeline.py  # Main FastAPI application
│   ├── lottery_checker.py     # Prize matching algorithm
│   ├── lottery_scheduler.py   # Daily scraper scheduler
│   └── lottery_scraper.py     # Web scraping logic
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # AuthContext for state
│   │   ├── hooks/             # Custom React hooks
│   │   └── App.jsx            # Main application
│   └── public/                # Static assets
│
├── model_training/             # AI/ML pipeline
│   ├── pipeline.py            # YOLO + OCR processing
│   ├── dataset/               # Training data (150 images)
│   └── trained model2/        # YOLOv11n weights
│
├── database/
│   └── init.sql               # PostgreSQL schema
│
├── docker-compose.yaml        # PostgreSQL container config
├── package.json               # Root scripts (run both servers)
└── .env                       # Environment variables (create this)
```

---

## 📦 Prerequisites

Before installation, ensure you have:

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Node.js 20+** & npm ([Download](https://nodejs.org/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **Git** ([Download](https://git-scm.com/))
- **8GB+ RAM** (for YOLO model + EasyOCR)
- **Windows 10/11**, **macOS**, or **Linux**

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://git.itim.vn/coccoc/lotto-ai.git
cd LottoAI
```

### 2. Backend Setup

```bash
# Create Python virtual environment
python -m venv .venv312

# Activate virtual environment
# Windows:
.venv312\Scripts\activate
# macOS/Linux:
source .venv312/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn python-multipart pillow numpy opencv-python
pip install ultralytics easyocr psycopg2-binary python-dotenv
pip install python-jose[cryptography] argon2-cffi
pip install requests beautifulsoup4 apscheduler pytz
```

### 3. Frontend Setup

```bash
# Install root dependencies (concurrently)
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Database Setup

```bash
# Start PostgreSQL container
docker-compose up -d

# Verify database is running
docker ps
```

The database will automatically initialize with the schema from `database/init.sql`.

---

## ⚙️ Configuration

### 1. Create `.env` File

Create a `.env` file in the project root:

```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=lottoai_db
POSTGRES_USER=lottoai_user
POSTGRES_PASSWORD=your_secure_password_here

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# Google OAuth (optional, for social login)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### 2. Generate Secure Keys

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate secure PostgreSQL password
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

### 3. Google OAuth Setup (Optional)

If you want to enable Google login:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
6. Copy Client ID and Secret to `.env`

---

## 🏃 Running the Application

### Option 1: Run Everything Together (Recommended)

```bash
# From project root
npm run dev
```

This starts:
- Frontend dev server on `http://localhost:5173`
- Backend API server on `http://localhost:8000`
- Lottery scraper scheduler (runs daily at 4:45pm)

### Option 2: Run Separately

**Terminal 1 - Backend:**
```bash
python -u -m uvicorn backend.fastapi_yoloocr_pipeline:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Accessing the Application

- **Frontend UI**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 📚 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/signup` | POST | Create new account | No |
| `/auth/login` | POST | Login with credentials | No |
| `/auth/me` | GET | Get current user info | Yes (JWT) |
| `/auth/google` | GET | Initiate Google OAuth | No |
| `/auth/google/callback` | GET | OAuth callback handler | No |

### Core Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/upload/` | POST | Upload & verify ticket | Optional |
| `/upload/debug/` | GET | Upload form (debug mode) | No |

### Request Examples

**Sign Up:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securePassword123"
  }'
```

**Upload Ticket:**
```bash
curl -X POST http://localhost:8000/upload/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@ticket.jpg"
```

**Response Example:**
```json
{
  "status": "success",
  "filename": "ticket.jpg",
  "extracted_number": "127333",
  "prize_check": {
    "matched_prizes": ["4"],
    "is_winner": true,
    "draw_info": {
      "draw_date": "2025-11-20",
      "region": "Đồng Nai"
    },
    "winning_numbers": {
      "prize_8": "53",
      "prize_7": "502",
      "prize_4": ["97617", "54133", "96888", "41173", "98427", "32652", "05180"],
      "jp": "300167"
    }
  }
}
```

For complete API documentation, visit: http://localhost:8000/docs

---

## 🗄️ Database Schema

### Tables

**users** - User accounts
```sql
id              SERIAL PRIMARY KEY
email           VARCHAR(255) UNIQUE NOT NULL
username        VARCHAR(100) UNIQUE NOT NULL
password_hash   VARCHAR(255)          -- NULL for OAuth users
oauth_provider  VARCHAR(50)           -- 'google', etc.
oauth_id        VARCHAR(255)
is_active       BOOLEAN DEFAULT TRUE
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**user_numbers** - Uploaded lottery numbers
```sql
id          SERIAL PRIMARY KEY
user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE
user_number VARCHAR(10) NOT NULL
created_at  TIMESTAMP
```

**winning_numbers** - Daily lottery results
```sql
id              SERIAL PRIMARY KEY
draw_date       DATE NOT NULL
region          VARCHAR(30)
prize_8         VARCHAR(10)           -- 2 digits
prize_7         VARCHAR(10)           -- 3 digits
prize_6         TEXT[]                -- 4 digits, multiple winners
prize_5         VARCHAR(10)           -- 4 digits
prize_4         TEXT[]                -- 5 digits, multiple winners
prize_3         TEXT[]                -- 5 digits, multiple winners
prize_2         VARCHAR(10)           -- 5 digits
prize_1         VARCHAR(10)           -- 5 digits
jp_consolation  VARCHAR(10)           -- 5 digits (last 5 of jackpot)
jp              VARCHAR(10)           -- 6 digits (jackpot)
created_at      TIMESTAMP
```

### Relationships

- **users** ↔ **user_numbers**: One-to-Many (one user can upload multiple numbers)
- **winning_numbers**: Independent table, updated daily by scraper

---

## 🚢 Deployment

### Production Deployment on Linux Server

See detailed deployment guide: [backend/README.md#deployment](backend/README.md#deployment)

**Quick Steps:**

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Python & Node.js
sudo apt install -y python3 python3-venv python3-pip nodejs npm
```

2. **Clone & Configure**
```bash
git clone https://github.com/your-username/LottoAI.git
cd LottoAI
cp .env.example .env
nano .env  # Update with production values
```

3. **Build & Run**
```bash
# Start database
docker-compose up -d

# Setup backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with PM2 (process manager)
npm install -g pm2
pm2 start "python -u -m uvicorn backend.fastapi_yoloocr_pipeline:app --host 0.0.0.0" --name lottoai-backend

# Build frontend
cd frontend
npm install
npm run build

# Serve with Nginx (configure reverse proxy)
```

4. **SSL Setup**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Docker PostgreSQL won't start**
```bash
# Check if port 5433 is in use
netstat -an | grep 5433

# Stop existing PostgreSQL services
sudo systemctl stop postgresql

# Restart Docker container
docker-compose down
docker-compose up -d
```

**Issue: YOLO model download fails**
```bash
# Manually download model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo11n.pt
mv yolo11n.pt model_training/
```

**Issue: EasyOCR language download fails**
```bash
# Download English model manually
mkdir -p ~/.EasyOCR/model
# Download from: https://github.com/JaidedAI/EasyOCR/releases
```

**Issue: Frontend can't connect to backend**
```bash
# Check CORS settings in backend/fastapi_yoloocr_pipeline.py
# Ensure frontend URL is in allow_origins list
```

**Issue: JWT token expired**
```bash
# Token expires after 7 days
# User needs to login again
# Adjust expiration in backend/auth.py: ACCESS_TOKEN_EXPIRE_MINUTES
```

### Debug Mode

Enable debug logging:
```bash
# Backend
export LOG_LEVEL=DEBUG
python -m uvicorn backend.fastapi_yoloocr_pipeline:app --reload --log-level debug

# Frontend
npm run dev  # Already in debug mode with hot reload
```

### Database Inspection

```bash
# Connect to PostgreSQL
docker exec -it lottoai_db_postgres psql -U lottoai_user -d lottoai_db

# Useful queries
\dt  # List tables
SELECT * FROM users;
SELECT * FROM winning_numbers ORDER BY draw_date DESC LIMIT 5;
\q  # Exit
```

---

## 🤝 Contributing

### Development Workflow

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and test**
```bash
# Run tests (if available)
pytest backend/

# Check linting
flake8 backend/
eslint frontend/src/
```

3. **Commit with meaningful messages**
```bash
git add .
git commit -m "feat: add user profile page"
```

4. **Push and create Pull Request**
```bash
git push origin feature/your-feature-name
```

## 📄 License

This project is proprietary software developed for Cốc Cốc. All rights reserved.

For internal use only. Distribution, modification, or use outside the company requires explicit permission.

---

## 📞 Support

For questions or issues:
- **Mentor**: [Mr.Tu Thanh Tung] - [tungtt1@coccoc.com]
- **Documentation**: See directory-specific READMEs:
  - [Backend Documentation](backend/README.md)
  - [Frontend Documentation](frontend/README.md)
  - [ML Pipeline Documentation](model_training/README.md)

*Last Updated: November 2025*
