# fastapi_yoloocr_pipeline.py
# run the program at the root folder with: python -m uvicorn backend.fastapi_yoloocr_pipeline:app --reload
# Access debug mode through: http://127.0.0.1:8000/upload/debug/
# Else: http://127.0.0.1:8000/upload/
# Run npm run dev:backend & navigate to http://127.0.0.1:8000/docs to test out all endpoints

# ---------- Libraries ---------
from contextlib import asynccontextmanager
from backend.lottery_scheduler import start_scheduler
from fastapi import FastAPI, UploadFile, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, FileResponse
from model_training.pipeline import process_single_image
from backend.lottery_checker import check_user_prizes
from backend.auth_routes import router as auth_router
from backend.auth import get_optional_user_id
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, cv2, psycopg2
import numpy as np
import logging

# ---------- Path / Directories ----------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
FORM_FILE = os.path.join(FRONTEND_DIR, "form.html")
FORM_DEBUG_FILE = os.path.join(FRONTEND_DIR, "form_debug.html")

# Only for debugging 
RECEIVING_DIR = r"C:\Users\Hayden Duong\Desktop\LottoAI\backend\received_folder"
os.makedirs(RECEIVING_DIR, exist_ok=True)

# ---------- Load .env file ----------
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ 
    Lifespan event handler for startup and shutdown
    """
    # ========== STARTUP CODE ==========
    # This runs ONCE when FastAPI app starts
    # Start scheduler
    # Connect to db
    # Load ML models
    scheduler = start_scheduler()
    logging.info("Lottery scheduler started")
    
    # Application request-handling period
    yield
    
    # ========== SHUTDOWN CODE ==========
    # This run ONCE when FastAPI app stops (Ctrl + C or due to crash)
    # Stop scheduler
    scheduler.shutdown()
    logging.info("Lottery scheduler stopped") 

# ---------- FastAPI App Initialization with lifespan ----------
app = FastAPI(lifespan=lifespan)

# Add CORS middlewares to prevent the blockage of CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # React dev server
        "http://127.0.0.1:5137",
        "http://localhost:3000",    # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],            # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],            # Allow all headers
)

# Register authentication routes to FastAPI application
app.include_router(auth_router)

# ---------- Helper Function ----------
def get_db_connection():
    """
    Purpose: Establish connection to PostgreSQL database

    Returns:
        psycopg2.connection: Database connection object
    
    Raises:
        HTTPException: If connection fails
    """
    # password = os.getenv("POSTGRES_PASSWORD")
    
    # # Debug: Show password length and first/last char
    # print(f"Password length: {len(password)}")
    # print(f"Password (masked): {password[0]}{'*' * (len(password)-2)}{password[-1]}")
    
    try:
        conn = psycopg2.connect(
            host = os.getenv("POSTGRES_HOST"),
            port = int(os.getenv("POSTGRES_PORT")),
            user = os.getenv("POSTGRES_USER"),
            password = os.getenv("POSTGRES_PASSWORD"),
            database = os.getenv("POSTGRES_DB")
        )
        
        logging.info("Connected successfully to Docker-PostgreSQL")
        
        return conn
    
    except psycopg2.OperationalError as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException ( status_code = 503, detail = "Database service unavailable. Please try again")
       
# ---------- GET Endpoints ----------
# Standard endpoints
@app.get("/upload/", response_class = HTMLResponse)
async def upload_form():
    return FileResponse(FORM_FILE, media_type = "text/html")

@app.get("/upload/debug/", response_class = HTMLResponse)
async def upload_form():
    return FileResponse(FORM_DEBUG_FILE, media_type = "text/html")

@app.post("/upload/")
async def uploadfile(
    file: UploadFile, 
    debug: str = Query("false"), 
    user_id: Optional[int] = Depends(get_optional_user_id)
    ):
    """
    Handle file upload and calling YOLO & EasyOCR pipeline for extracting serial number
    
    Flow:
    1. Receive uploaded file from user input.
    2. Convert bytes to numpy array image form.
    3. Run through the pipeline.
    4. Return results as JSON
    
    Note:
    . Uploaded image sent via (debug) "/upload/?debug=true" - "?debug=true" is query parameter
    . FastAPI will extract these automatically (based on the input parameters: file & debug)
    1. file = the uploaded file from form (form.html / form_debug.html)
    2. debug = "true" (from ?debug=true in the URL)   
    """
    
    try:
        # ---------- Uploaded File Validation Test ----------
        # Validate input file - to make sure there is a file for later processing
        if file.filename == "":
            raise HTTPException(status_code = 400, detail = "No file is selected")

        # Check for file size (maximum 10MB)
        # FastAPI UploadFile ".read()" will return a byte stream which can be used with len() for determine the size of input file
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code = 413, detail = "File to large (over 10 MB)")
        
        # Check for valid file-extension
        # Since file-extension allowance from the UI-side is not strong enough (security-issue)
        # Thus, additional file-extension is required in the backend
        allowed_extension = {'.jpg', '.jpeg'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extension:
            raise HTTPException(
                status_code = 400,
                detail = f"Invalid file type. Allowed: {', '.join(allowed_extension)}"
            )
        
        logging.info(f"Received file: {file.filename}")
        logging.info(f"Size of this file: {len(content) / 1024:.2f} KB")
        
        # ---------- Converting bytes (byte stream) into numpy array before sending it to the pipeline ----------
        # Current 'content' is in byte stream, e.g: b'\xff\xd8\xff\xe0\x00\x10JFIF...'
        # np.frombuffer() will creates a Numpy array that views the raw bytes as numeric data
        # where each byte becomes an unsigned integer, or non-negative (0-255) 
        # nparr will have a structure of (Numpy Array) 1D array of pixel data, but not yet a real image
        nparr = np.frombuffer(content, np.uint8)
        
        # cv2.imdecode() will interprets the 1D array nparr into encoded image format (JPEG, PNG, etc.)
        # Then decodes into a regular OpenCV image - a Numpy array of shape (3D Numpy array: height, width, channels)
        # This function is similar to cv2.imread(), but, it happens in memory
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code = 400, detail = "Could not decode the image")
        
        logging.info(f"Image dimension: {image.shape[0]} x {image.shape[1]} pixels")
        
        # ---------- Process Image with Pipeline ----------
        pipeline_result = process_single_image(image, file.filename)
        
        if not pipeline_result["success"] or len(pipeline_result["detections"]) == 0:
            return {
                "status": "error",
                "filename": file.filename,
                "message": "No serial number detected in image"
            }
        
        extracted_digits = pipeline_result["detections"][0]["extracted_digits"]
        
        if not extracted_digits or extracted_digits.strip() == "":
            return {
                "status": "error",
                "filename": file.filename,
                "message": "OCR failed to extract serial number"
            }
        
        # Converting str value "true" to Bool True
        is_debug = (debug.lower() == "true")
        
        # ---------- Winning Number Checking ----------
        logging.info("STAGE 4: Connecting to Docker-PostgreSQL container to retrieve and comparing for winning number")
        prize_result = check_user_prizes(extracted_digits)
        
        if user_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_numbers (user_id, user_number)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, user_number) WHERE user_id IS NOT NULL DO NOTHING
                    """,
                    (user_id, extracted_digits)
                )
                
                conn.commit()
                
                cursor.close()
                conn.close()
                
                logging.info(f"Saved number {extracted_digits} for user {user_id}")
                
            except Exception as e:
                logging.error(f"Could not save to database: {e}")
                
        else:
            logging.info("Guest upload - not saving to database")
        
        # ---------- Return Results ----------
        # If (/?debug=true) then applying these changes
        if is_debug:
            # Store uploaded image on server storage
            saved_path = os.path.join(RECEIVING_DIR, file.filename)
            with open(saved_path, "wb") as f:
                    f.write(content)
            logging.info(f"File saved to {saved_path}")
        
            # ---------- Return results ----------
            return {
                "status": "success",
                "filename": file.filename,
                "file_size_kb": len(content) / 1024,
                "image_dimension": {
                    "width": image.shape[1],
                    "height": image.shape[0]
                },
                "pipeline_results": pipeline_result,
                "prize_check": prize_result
            }
        else:
            return {
                "extracted_digits": extracted_digits,
                "prize_check": prize_result
            }
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        logging.exception("Unexpected error while processing uploaded ticket.")
        
        raise HTTPException(
            status_code=500,
            detail="Unable to process ticket"
        )