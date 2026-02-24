# yolo_easyocr_pipeline.py

# ---------- Libraries ----------
from ultralytics import YOLO
import easyocr
import re
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# ---------- Configuration ----------
YOLO_WEIGHTS = Path(r"C:\Users\Hayden Duong\Desktop\LottoAI\model_training\trained model2\weights\best.pt")
INPUT_DIR = Path(r"C:\Users\Hayden Duong\Desktop\LottoAI\model_training\raw_images\new_images")
OUTPUT_DIR = Path(r"C:\Users\Hayden Duong\Desktop\LottoAI\model_training\testing")
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_PATH = OUTPUT_DIR / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

READ_LANGUAGE = ['en']
MIN_CONFIDENCE = 0.30
DIGIT_REGEX = re.compile(r'\d+')

# ---------- Functions ----------
def clean_text_digits(text):
    # Extract digits only
    digits = DIGIT_REGEX.findall(text)
    return ''.join(digits)

def main():
    
    # Initialize YOLO and EasyOCR
    print("Loading YOLO model and EasyOCR reader...")
    model = YOLO(str(YOLO_WEIGHTS))
    reader = easyocr.Reader(READ_LANGUAGE)
    
    # Prepare CSV
    csv_fields = ["image_path", "det_class", "det_conf", "bbox_xyxy", "ocr_raw_text", "ocr_conf", "ocr_digits"]
    rows = []
    
    # Run YOLO detection on all images
    print("\n" + "="*60)
    print("STAGE 1: YOLO DETECTION")
    print("="*60)
    
    results = model.predict(
        source=str(INPUT_DIR),
        conf=MIN_CONFIDENCE,
        save=False,
        verbose=True
    )
    
    # Process YOLO results and run OCR on detected crops
    print("\n" + "="*60)
    print("STAGE 2: OCR ON DETECTED REGIONS")
    print("="*60)
    
    image_paths = sorted(INPUT_DIR.glob("*.*"))
    
    for img_path, result in zip(image_paths, results):
        
        # Read original image
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            print(f"Failed to read {img_path.name}, skipping.")
            continue
        
        # img_h, img_w = img_bgr.shape[:2]
        
        # Get YOLO boxes
        boxes = getattr(result, 'boxes', None)
        if boxes is None or len(boxes) == 0:
            print(f"No detections in {img_path.name}")
            continue
        
        try:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy() if hasattr(boxes, 'conf') else np.ones(len(xyxy))
            cls_ids = boxes.cls.cpu().numpy().astype(int) if hasattr(boxes, 'cls') else np.zeros(len(xyxy), dtype=int)
        except:
            xyxy = np.array(boxes.xyxy)
            confs = np.array(boxes.conf) if hasattr(boxes, 'conf') else np.ones(len(xyxy))
            cls_ids = np.array(boxes.cls, dtype=int) if hasattr(boxes, 'cls') else np.zeros(len(xyxy), dtype=int)
        
        # Process each detection
        for i, (box, conf, cls_id) in enumerate(zip(xyxy, confs, cls_ids)):
            
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Skip low confidence
            if conf < MIN_CONFIDENCE:
                continue
            
            # Crop region directly from image (NO DISK I/O)
            crop = img_bgr[y1:y2, x1:x2]
            
            # Run OCR directly on the crop (in memory, no file saving)
            try:
                ocr_results = reader.readtext(crop, detail=1)
            except Exception as e:
                print(f"  OCR error on {img_path.name} box {i}: {e}")
                ocr_results = []
            
            # Extract text and confidence
            if ocr_results:
                combined_text = " ".join([text for (_, text, _) in ocr_results])
                avg_conf = float(np.mean([confidence for (_, _, confidence) in ocr_results]))
            else:
                combined_text = ""
                avg_conf = 0.0
            
            digits = clean_text_digits(combined_text)
            
            # Save result
            rows.append({
                "image_path": str(img_path),
                "det_class": str(cls_id),
                "det_conf": float(conf),
                "bbox_xyxy": f"{x1},{y1},{x2},{y2}",
                "ocr_raw_text": combined_text,
                "ocr_conf": avg_conf,
                "ocr_digits": digits
            })
            
            print(f"  ✓ Box {i}: {img_path.name} → Digits: {digits} (conf: {avg_conf:.2f})")
    
    # Save to CSV
    print("\n" + "="*60)
    if rows:
        df = pd.DataFrame(rows, columns=csv_fields)
        df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
        print(f"✅ Saved {len(rows)} results to: {CSV_PATH}")
    else:
        print("❌ No results to save")
    print("="*60)

if __name__ == "__main__":
    main()