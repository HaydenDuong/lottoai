# Model Training - AI/ML Pipeline

This directory contains the computer vision pipeline for lottery ticket detection and number extraction using YOLOv11n and EasyOCR.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Dataset Structure](#dataset-structure)
- [Model Training](#model-training)
- [Pipeline Components](#pipeline-components)
- [Performance Metrics](#performance-metrics)
- [Usage](#usage)
- [Retraining the Model](#retraining-the-model)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The AI/ML pipeline consists of two main stages:

1. **Object Detection (YOLO)**: Detects lottery ticket region in uploaded images
2. **Optical Character Recognition (EasyOCR)**: Extracts 6-digit numbers from detected regions

**Why This Approach?**
- **Accuracy**: Two-stage approach ensures precise number extraction
- **Robustness**: Handles various image conditions (lighting, angle, background)
- **Speed**: Optimized for real-time processing (< 3 seconds)
- **Scalability**: Can be extended to detect multiple regions (date, prize type, etc.)

---

## 🏗️ Pipeline Architecture

```
┌──────────────────────────────────────────────────────┐
│           Input: Image (bytes/NumPy array)           │
└────────────────────┬─────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │     OpenCV (cv2.imdecode)  │
        │  Convert bytes → NumPy     │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │   STAGE 1: YOLO Detection  │
        │   • Load model (YOLOv11n)  │
        │   • Detect ROI (serial)    │
        │   • Get bounding box       │
        │   • Confidence: 30%+       │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │  STAGE 2: NumPy Cropping   │
        │   • Extract coordinates    │
        │   • Add 10px padding       │
        │   • Crop: img[y1:y2, x1:x2]│
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │   STAGE 3: EasyOCR         │
        │   • Read text from crop    │
        │   • Extract all digits     │
        │   • Clean with regex       │
        │   • Return 6-digit number  │
        └────────────┬───────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │    Output: Extracted Number │
        │    + Confidence Score       │
        │    + Bounding Box Coords    │
        └─────────────────────────────┘
```

---

## 📁 Dataset Structure

```
model_training/
├── dataset/
│   ├── train/                    # Training data (100 images)
│   │   ├── images/
│   │   │   ├── ticket_001.png
│   │   │   ├── ticket_002.png
│   │   │   └── ... (100 total)
│   │   ├── labels/               # YOLO format annotations
│   │   │   ├── ticket_001.txt
│   │   │   ├── ticket_002.txt
│   │   │   └── ... (100 total)
│   │   ├── classes.txt           # Class names
│   │   └── labels.cache          # YOLO cache file
│   │
│   ├── val/                      # Validation data (20 images)
│   │   ├── images/
│   │   ├── labels/
│   │   ├── classes.txt
│   │   └── labels.cache
│   │
│   └── test/                     # Test data (30 images)
│       └── images/
│
├── trained model2/               # Final trained model
│   ├── weights/
│   │   ├── best.pt              # Best model weights (used in production)
│   │   └── last.pt              # Last epoch weights
│   ├── results.csv               # Training metrics
│   ├── confusion_matrix.png
│   └── ... (other metrics)
│
├── raw_images/                   # Original unprocessed images
│   ├── lottery_tickets/          # Collected ticket images
│   └── real_images/              # Real-world test images
│
├── pipeline.py                   # Main inference pipeline
├── model_training.py             # Training script
├── data.yaml                     # YOLO dataset configuration
├── yolo11n.pt                    # Pretrained YOLO base model
└── README.md                     # This file
```

---

## 📊 Dataset Details

### Training Set
- **Size**: 100 images
- **Format**: PNG (primarily)
- **Resolution**: Variable (resized during training)
- **Annotations**: YOLO format (normalized coordinates)

### Validation Set
- **Size**: 20 images
- **Purpose**: Monitor overfitting during training
- **Split**: 20% of total data

### Test Set
- **Size**: 30 images
- **Purpose**: Final model evaluation
- **No labels**: Used only for inference testing

### Class Definition

**`classes.txt`:**
```
serial_zone
```

Currently, only one class is defined: the serial number region of the lottery ticket.

**Future Enhancement:** Add more classes like `date_zone`, `prize_type_zone`, `barcode`, etc.

---

### YOLO Annotation Format

**Example: `ticket_001.txt`**
```
0 0.512 0.348 0.426 0.084
```

**Format:** `class_id center_x center_y width height`

- **class_id**: 0 (serial_zone)
- **center_x**: 0.512 (normalized, 0-1)
- **center_y**: 0.348 (normalized, 0-1)
- **width**: 0.426 (normalized, 0-1)
- **height**: 0.084 (normalized, 0-1)

All coordinates are normalized relative to image dimensions.

---

## 🎓 Model Training

### Base Model

**YOLOv11n** (nano version)
- Fastest variant of YOLO11
- Optimized for real-time inference
- Pretrained on COCO dataset
- Fine-tuned on lottery ticket dataset

### Training Configuration

**`data.yaml`:**
```yaml
path: C:\Users\Hayden Duong\Desktop\LottoAI\model_training\dataset
train: train/images
val: val/images
test: test/images

nc: 1  # Number of classes
names: ['serial_zone']
```

### Training Process

**Script:** `model_training.py`

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolo11n.pt')

# Train on custom dataset
results = model.train(
    data='data.yaml',
    epochs=100,                  # Number of training epochs
    imgsz=640,                   # Image size
    batch=16,                    # Batch size
    patience=10,                 # Early stopping patience
    save=True,                   # Save checkpoints
    device='cuda',               # GPU acceleration (or 'cpu')
    workers=4,                   # Data loading workers
    project='trained model2',    # Output directory
    name='weights',              # Experiment name
    exist_ok=True                # Overwrite existing
)
```

### Training Command

```bash
# Activate virtual environment
source .venv312/bin/activate  # or .venv312\Scripts\activate on Windows

# Run training
python model_training/model_training.py
```

**Training Time:**
- **GPU (NVIDIA RTX 3060)**: ~30 minutes for 100 epochs
- **CPU (Intel i7)**: ~3-4 hours for 100 epochs

---

### Training Metrics

**Output Files:**

1. **`best.pt`**: Model with lowest validation loss
2. **`last.pt`**: Model from final epoch
3. **`results.csv`**: Epoch-by-epoch metrics
4. **`confusion_matrix.png`**: Confusion matrix visualization
5. **`BoxP_curve.png`**: Precision curve
6. **`BoxR_curve.png`**: Recall curve
7. **`BoxF1_curve.png`**: F1 score curve

**Key Metrics:**

| Metric | Value | Description |
|--------|-------|-------------|
| **Precision** | 0.92 | % of detections that are correct |
| **Recall** | 0.89 | % of ground truth boxes detected |
| **mAP50** | 0.91 | Mean Average Precision at IoU=0.5 |
| **mAP50-95** | 0.68 | Mean AP across IoU thresholds |

---

## 🔧 Pipeline Components

### 1. `pipeline.py` - Inference Pipeline

**Purpose:** Process single images through YOLO + OCR pipeline.

**Key Constants:**

```python
YOLO_WEIGHTS = Path("model_training/trained model2/weights/best.pt")
READ_LANGUAGE = ['en']          # EasyOCR language
MIN_CONFIDENCE = 0.30           # YOLO confidence threshold
DIGIT_REGEX = re.compile(r'\d+')
```

---

### 2. Model Loading (Global)

**Why Global?**
- Models are loaded **once** when module is imported
- Reused for all subsequent requests
- Significantly improves performance

```python
# Loaded once on import
model = YOLO(str(YOLO_WEIGHTS))
reader = easyocr.Reader(READ_LANGUAGE)
```

**Performance Impact:**
- **With global loading**: 1-2 seconds per image
- **Without global loading**: 5-10 seconds per image (model loads each time)

---

### 3. Main Function: `process_single_image()`

**Signature:**
```python
def process_single_image(image_array: np.ndarray, filename: str = "unknown") -> dict
```

**Parameters:**
- `image_array`: NumPy array (height, width, channels) in BGR format
- `filename`: Original filename for logging

**Returns:**
```python
{
    "success": True,
    "detections": [
        {
            "bbox": [x1, y1, x2, y2],
            "confidence": 0.95,
            "class_id": 0,
            "extracted_digits": "123456",
            "ocr_confidence": 0.87,
            "crop_dimensions": [height, width]
        }
    ],
    "message": "Successfully extracted 1 serial number(s)"
}
```

---

### 4. YOLO Detection Stage

**Code:**
```python
# Stage 1: Run YOLO
result = model.predict(
    source=image_array,
    conf=MIN_CONFIDENCE,     # 0.30 threshold
    save=False,              # Don't save annotated images
    verbose=False            # Suppress console output
)

result = result[0]  # Extract first (only) result

# Extract bounding boxes
boxes = getattr(result, 'boxes', None)

if (boxes is None) or len(boxes) == 0:
    return {
        "success": False,
        "detections": [],
        "message": "No serial zone detected"
    }

# Convert torch tensors to NumPy
xyxy = boxes.xyxy.cpu().numpy()       # Bounding box coords
confs = boxes.conf.cpu().numpy()      # Confidence scores
cls_ids = boxes.cls.cpu().numpy()     # Class IDs
```

**Output:**
- **xyxy**: Array of shape (N, 4) where N = number of detections
  - Format: `[x1, y1, x2, y2]` (top-left and bottom-right corners)
- **confs**: Array of shape (N,) with confidence scores (0-1)
- **cls_ids**: Array of shape (N,) with class IDs (0 = serial_zone)

---

### 5. Cropping Stage

**Why Add Padding?**
- YOLO bounding box might be slightly tight
- OCR works better with some margin around text
- 10-pixel padding ensures no character clipping

```python
padding = 10

for box in xyxy:
    x1, y1, x2, y2 = box
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    # Add padding (with boundary checks)
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(image_array.shape[1], x2 + padding)
    y2 = min(image_array.shape[0], y2 + padding)
    
    # Crop using NumPy array slicing
    crop = image_array[y1:y2, x1:x2]
    crops_list.append(crop)
```

**Important:** NumPy uses `[rows, cols]` format = `[y, x]` format!

---

### 6. OCR Stage

**EasyOCR Configuration:**

```python
ocr_result = reader.readtext(
    crop,
    detail=1,          # Return bbox, text, confidence
    paragraph=False,   # Don't group into paragraphs
    batch_size=1       # Process one image at a time
)
```

**Output Format:**
```python
[
    (
        [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],  # Bounding box corners
        "123456",                                   # Recognized text
        0.87                                        # Confidence score
    ),
    # ... more detections if text is split
]
```

---

### 7. Text Cleaning

**Challenge:** EasyOCR might detect spaces, letters, or symbols.

**Solution:** Extract only digits using regex.

```python
def clean_text_digits(text):
    digits = DIGIT_REGEX.findall(text)  # ['123', '456']
    return ''.join(digits)               # '123456'
```

**Example:**
- Input: `"1 2 3 - 4 5 6"`
- Output: `"123456"`

---

### 8. Multi-Detection Handling

**If EasyOCR splits text:**
```python
ocr_result = [
    (..., "123", 0.9),
    (..., "456", 0.85)
]

# Combine all text
combined_text = " ".join([text for (_, text, _) in ocr_result])
# "123 456"

# Average confidence
avg_conf = np.mean([confidence for (_, _, confidence) in ocr_result])
# 0.875

# Clean digits
digits = clean_text_digits(combined_text)
# "123456"
```

---

## 📈 Performance Metrics

### Model Performance

**YOLO Detection:**
| Metric | Value |
|--------|-------|
| Precision | 92% |
| Recall | 89% |
| mAP@0.5 | 91% |
| Inference Speed | ~50ms/image (GPU) |

**EasyOCR Extraction:**
| Metric | Value |
|--------|-------|
| Accuracy | 85-95% (depends on image quality) |
| Speed | ~1-2s/image (CPU) |

---

### End-to-End Performance

**Total Pipeline:**
- **GPU**: ~1.5 seconds per image
- **CPU**: ~2.5 seconds per image

**Breakdown:**
1. YOLO detection: 50-100ms
2. NumPy cropping: <10ms
3. EasyOCR: 1-2 seconds (dominant factor)

---

### Factors Affecting Accuracy

**Positive Factors:**
- ✅ High-resolution images (> 800px width)
- ✅ Good lighting, minimal glare
- ✅ Ticket parallel to camera (minimal rotation)
- ✅ Clear, printed numbers (not handwritten)

**Negative Factors:**
- ❌ Low resolution (< 400px width)
- ❌ Heavy shadows or glare
- ❌ Extreme angles (> 45° rotation)
- ❌ Crumpled or damaged tickets

---

## 🚀 Usage

### Basic Usage (Standalone)

```python
from model_training.pipeline import process_single_image
import cv2

# Load image
image = cv2.imread('ticket.jpg')

# Process
result = process_single_image(image, 'ticket.jpg')

# Check result
if result['success']:
    for detection in result['detections']:
        print(f"Number: {detection['extracted_digits']}")
        print(f"Confidence: {detection['confidence']:.2f}")
else:
    print(f"Error: {result['message']}")
```

---

### Integration with FastAPI

**In `backend/fastapi_yoloocr_pipeline.py`:**

```python
from model_training.pipeline import process_single_image

@app.post("/upload/")
async def upload_file(file: UploadFile):
    # Read file bytes
    content = await file.read()
    
    # Convert to NumPy array
    nparr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Process with pipeline
    result = process_single_image(image, file.filename)
    
    return result
```

---

### Batch Processing

```python
import os
from pathlib import Path

def process_directory(input_dir, output_csv):
    results = []
    
    for img_file in Path(input_dir).glob('*.jpg'):
        image = cv2.imread(str(img_file))
        result = process_single_image(image, img_file.name)
        
        if result['success']:
            for det in result['detections']:
                results.append({
                    'filename': img_file.name,
                    'number': det['extracted_digits'],
                    'confidence': det['confidence']
                })
    
    # Save to CSV
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    
    return df
```

---

## 🔄 Retraining the Model

### When to Retrain

Retrain the model when:
- ✅ Adding new ticket designs (different layouts)
- ✅ Expanding to new regions/lottery types
- ✅ Detection accuracy drops below 85%
- ✅ Adding new classes (date zone, prize type, etc.)

---

### Step 1: Collect More Images

**Target:** 150+ images per class

**Sources:**
- Real ticket photos
- Scanned images
- Synthetically generated images

**Best Practices:**
- Vary lighting conditions
- Include different angles (0-30° rotation)
- Mix of clean and slightly worn tickets
- Different backgrounds

---

### Step 2: Annotate Images

**Tools:**
- [LabelImg](https://github.com/heartexlabs/labelImg) - Desktop annotation tool
- [Roboflow](https://roboflow.com/) - Online annotation platform
- [CVAT](https://cvat.org/) - Advanced annotation tool

**Process:**
1. Load image in annotation tool
2. Draw bounding box around serial number region
3. Label as `serial_zone`
4. Export in YOLO format
5. Place in `dataset/train/` or `dataset/val/`

---

### Step 3: Update `data.yaml`

```yaml
path: C:\Path\To\LottoAI\model_training\dataset
train: train/images
val: val/images

nc: 1  # Update if adding more classes
names: ['serial_zone']  # Update with new class names
```

---

### Step 4: Adjust Training Parameters

**For larger dataset (200+ images):**
```python
results = model.train(
    data='data.yaml',
    epochs=150,          # More epochs
    batch=32,            # Larger batch (if GPU allows)
    patience=20,         # More patience before early stop
    imgsz=640
)
```

**For more classes:**
```python
# Update nc in data.yaml
nc: 3
names: ['serial_zone', 'date_zone', 'prize_type']
```

---

### Step 5: Evaluate & Compare

```python
# Evaluate on test set
metrics = model.val(data='data.yaml', split='test')

# Compare with old model
print(f"New mAP: {metrics.box.map}")
print(f"Old mAP: 0.91")  # From previous training

# Test on real images
test_images = Path('model_training/raw_images/real_images')
for img in test_images.glob('*.jpeg'):
    result = process_single_image(cv2.imread(str(img)))
    # Check if results improved
```

---

### Step 6: Deploy New Model

```bash
# Backup old model
mv "model_training/trained model2/weights/best.pt" \
   "model_training/trained model2/weights/best_backup.pt"

# Copy new model
cp "runs/detect/train/weights/best.pt" \
   "model_training/trained model2/weights/best.pt"

# Restart server
pm2 restart lottoai-backend
```

---

### Issue: EasyOCR Language Model Not Found

**Error:**
```
Downloading detection model, please wait...
URLError: <urlopen error [Errno 11001] getaddrinfo failed>
```

**Solution:**
```bash
# Download English model manually
mkdir -p ~/.EasyOCR/model
cd ~/.EasyOCR/model

# Download from GitHub releases
# https://github.com/JaidedAI/EasyOCR/releases
```

---

### Issue: CUDA Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory. Tried to allocate 512.00 MiB
```

**Solution:**
```python
# Reduce batch size
model.train(batch=8)  # Instead of 16

# Or use CPU
model.train(device='cpu')
```

---

### Issue: Low Detection Accuracy

**Symptoms:**
- YOLO misses tickets in images
- Incorrect bounding boxes

**Solutions:**

1. **Lower confidence threshold:**
```python
MIN_CONFIDENCE = 0.20  # Instead of 0.30
```

2. **Collect more training data:**
- Focus on cases where detection fails
- Add similar images to training set

3. **Increase image size:**
```python
model.train(imgsz=800)  # Instead of 640
```

---

### Issue: Low OCR Accuracy

**Symptoms:**
- Correct detection but wrong digits extracted
- Missing digits in output

**Solutions:**

1. **Check image quality:**
```python
# Ensure crop is large enough
logging.info(f"Crop dimensions: {crop.shape}")
# Should be at least 50x200 pixels
```

2. **Adjust OCR parameters:**
```python
ocr_result = reader.readtext(
    crop,
    detail=1,
    width_ths=0.5,     # Lower for wider spacing
    paragraph=False,
    allowlist='0123456789'  # Only digits
)
```

3. **Preprocess crop:**
```python
# Increase contrast (only if needed)
import cv2
crop = cv2.convertScaleAbs(crop, alpha=1.5, beta=10)
```

---

## 🎓 Key Takeaways

1. **Simplicity is Strength**: Minimal preprocessing (no grayscale, rotation, etc.) works better with modern AI
2. **Two-Stage Pipeline**: YOLO for detection + EasyOCR for extraction is more accurate than end-to-end OCR
3. **Global Model Loading**: Load models once, reuse for all requests (10x speed improvement)
4. **NumPy for Cropping**: Pure NumPy slicing is faster and simpler than OpenCV cropping
5. **Confidence Thresholds Matter**: Balance between false positives (too low) and missed detections (too high)

---
