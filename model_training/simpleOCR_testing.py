import easyocr
import os
import re
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# ---------- Configuration ----------
INPUT_DIR = Path(r"C:\Users\Hayden Duong\Desktop\LottoAI\model_training\prediction\crops\serial_zone")
OUTPUT_DIR = Path(r"C:\Users\Hayden Duong\Desktop\LottoAI\model_training\testing")

CSV_PATH = OUTPUT_DIR / f"simple_ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

READ_LANGUAGE = ['en']
DIGIT_REGEX = re.compile(r'\d+')

# ---------- Functions ----------
def clean_text_digits(text):
    # Extract digits only
    digits = DIGIT_REGEX.findall(text)
    return ''.join(digits)

def main():
    """
    Main pipeline:
    1. Load all images from INPUT_DIR
    2. Run EasyOCR on each image
    3. Extract and clean text
    4. Save results to CSV
    """
    
    # Initialize OCR reader
    print("Initializing EasyOCR reader...")
    reader = easyocr.Reader(READ_LANGUAGE)
    
    # Prepare CSV
    csv_fields = ["image_path", "ocr_raw_text", "ocr_conf", "ocr_digits"]
    rows = []
    
    # Get all images
    image_paths = sorted(INPUT_DIR.glob("*.*"))
    print(f"Found {len(image_paths)} images to process\n")
    
    if len(image_paths) == 0:
        print(f"⚠️  No images found in {INPUT_DIR}")
        return
    
    # Loop through every image
    for idx, img_path in enumerate(image_paths, 1):
        
        # Read image
        img_bgr = cv2.imread(str(img_path))
        
        if img_bgr is None:
            print(f"[{idx}/{len(image_paths)}] ❌ Failed to read {img_path.name}, skipping.")
            continue
        
        # Run OCR directly on image
        try:
            ocr_results = reader.readtext(str(img_path))  # Returns (bbox, text, confidence)
        except Exception as e:
            print(f"[{idx}/{len(image_paths)}] ⚠️  OCR error on {img_path.name}: {e}")
            ocr_results = []
        
        # Combine OCR results
        combined_text = " ".join([text for (_, text, _) in ocr_results]) if ocr_results else ""
        avg_conf = float(np.mean([conf for (_, _, conf) in ocr_results])) if ocr_results else 0.0
        digits = clean_text_digits(combined_text)
        
        # Add to results
        rows.append({
            "image_path": str(img_path),
            "ocr_raw_text": combined_text,
            "ocr_conf": avg_conf,
            "ocr_digits": digits
        })
        
        # Print progress
        print(f"[{idx}/{len(image_paths)}] ✓ Processed {img_path.name} → Digits: {digits} (conf: {avg_conf:.2f})")
    
    # Save to CSV
    if rows:
        df = pd.DataFrame(rows, columns=csv_fields)
        df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
        print(f"\n✅ Saved {len(rows)} results to: {CSV_PATH}")
    else:
        print("\n❌ No results to save")

if __name__ == "__main__":
    main()