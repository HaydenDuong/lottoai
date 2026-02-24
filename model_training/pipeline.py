# pipeline.py
# ---------- Libraries ----------
from ultralytics import YOLO
import easyocr
import re
import numpy as np
from pathlib import Path
import logging

# ---------- Configuration Variables & Directories ----------
YOLO_WEIGHTS = Path(r"C:\Users\Hayden Duong\Desktop\LottoAI\model_training\trained model2\weights\best.pt")
READ_LANGUAGE = ['en']
MIN_CONFIDENCE = 0.30
DIGIT_REGEX = re.compile(r'\d+')

# ---------- Global Models (Only load once, Reusse many times) ----------
# Loaded once when the module is imported
logging.info("Loading both YOLO model & EasyOCR reader")
model = YOLO(str(YOLO_WEIGHTS))
reader = easyocr.Reader(READ_LANGUAGE)
logging.info("Models are loaded successfully.")

# ---------- Helper Functions ----------
def clean_text_digits(text):
    # Extract digits only
    digits = DIGIT_REGEX.findall(text)
    return ''.join(digits)

def process_single_image(image_array: np.ndarray, filename: str = "unknown"):
    try:
        # Check Step: determine if the passed in image does have valid value before proceeding
        if (image_array is None) or (image_array.size == 0):
            return {
                "success": False,
                "detections": [],
                "message": "Invalid or empty image"
            }
        
        logging.info(f"\n{'='*60}")
        logging.info(f"Processing: {filename}")
        logging.info(f"{'='*60}")
        
        # ---------- STAGE 1: YOLO DETECTION ----------
        logging.info("STAGE 1: Running YOLO Detection.....")
        
        # Processing input image with YOLO built-in ".predict" function to extract ROI (serial zone)
        result = model.predict(
            source = image_array,
            conf = MIN_CONFIDENCE,          
            save = False,                   # Not saving YOLO processed images on Server Storage
            verbose = False                 # verbose = True will display all related information of image_processing process to terminal console of Server
        )
        
        # YOLO always return output as a list from YOLO built-in function ".predict()", 
        # Thus, setting result = result[0] for one image processing still idealy and safe
        result = result[0]
        
        # getattr will try to extract an attribute from a value (if it has)
        # Purpose of this line: extract an attribute from a value and store that under a variable
        # output from YOLO built-in function ".predict()" will contain following attributes:
        # orig_img: np.ndarray -  the original image as a numpy array.
        # orig_shape: tuple - the original image shape in (height, width) format.
        # boxes: Boxes, optional - a Boxes object (a list) containing the detection bounding boxes, confidence scores, and class IDs of all detected objects inside the input image
        # masks: Masks, optional - A Masks object containing the detection masks.
        # probs: Probs, optional - A Probs object containing probabilities of each class for classification task.
        # keypoints: Keypoints, optional - A Keypoint object containing detected keypoint for each object.
        # obb: OBB, optional - An OBB object containing oriented bounding boxes.
        # speed: dict - A dictionary of preprocess, inference, and postprocess speeds in milliseconds per image,
        # names: dict - A dictionary mapping class indices to class names.
        # path: str - The path to the image file.
        # save_dir: str, optional Directory to save results.
        # Check further info: https://docs.ultralytics.com/modes/predict/#boxes
        boxes = getattr(result, 'boxes', None)      # if 'boxes' does not return any value, then, None will be assigned for 'boxes' as its value
        
        # Checking Step: determine if ROI is successfully extracted by trained YOLO model through checking 'boxes' value
        if (boxes is None) or len(boxes) == 0:
            
            logging.info(f"No detection is found from {filename}")
            
            return {
                "success": False,
                "detection": [],
                "message": f"Can't detect serial zone from {filename}"
            }
        
        # Extract bounding box data once it passed the Checking Step
        try:
            # boxes.xyxy will be in [x1, y1, x2, y2] PyTorch Tensor-format (torch.Tensor)
            # >>> boxes.xyxy
            # tensor([210.4, 140.2, 480.7, 180.3], (optional) device='cuda:0')
            # .cpu() will move data from GPU memory and copies it into CPU memory (RAM) for applying further with Python operations / libraries (still in torch.Tensor format)
            # .numpy() will converting now CPU-stored torch.Tensor into NumPy array (a native Python structure (numpy.ndarray) - integers (pixel coordinates)) for OpenCV cropping
            # Output:
            # array([210.4, 140.2, 480.7, 180.3])
            xyxy = boxes.xyxy.cpu().numpy()
            
            # Similar to boxes.xyxy, boxes.conf (confidence score of (each) detected box) is in torch.Tensor format
            # if hasattr(boxes, 'conf) will check if the boxes.conf does contain value:
            # if True, boxes.conf.cpu().numpy() to converting that torch.Tensor formatted value into Numpy array format
            # else, np.ones(len(xyxy)) will create a Numpy array based on len(xyxy) (based on how many bounding box elements present in boxes.xyxy) and fill with 1.0s
            # Since the program may not running if the value of 'conf' is empty, thus, setting to 1 served as safe placeholder.
            confs = boxes.conf.cpu().numpy() if hasattr(boxes, 'conf') else np.ones(len(xyxy))
            
            # Similar to 'boxes.conf' but with a typecast, class ID must be an integer !!!
            # Currently, serial_zone is set to be 0 and LottoAI detect only serial_zone
            # In other case, setting class ID to be 0 is by default (similar to why setting boxes.conf to 1 - for safe placeholder)
            cls_ids = boxes.cls.cpu().numpy().astype(int) if hasattr(boxes, 'cls') else np.zeros(len(xyxy), dtype=int)
        
        # Backup in case conversion from torch.Tensor to Numpy Array is failed
        # If 'boxes' is already in Numpy format (due to using YOLOv5/8 on CPU-only environment without torch tensors), then .cpu().numpy() will be failed
        except:
            xyxy = np.array(boxes.xyxy)
            confs = np.array(boxes.conf) if hasattr(boxes, 'conf') else np.ones(len(xyxy))
            cls_ids = np.array(boxes.cls, dtype=int) if hasattr(boxes, 'cls') else np.zeros(len(xyxy), dtype=int)
        
        # Display the number of detected bounding box (ROI)
        logging.info(f"Found {len(xyxy)} detection(s)")
        
        # ---------- STAGE 2: Processing image with YOLO's smart cropping ----------
        logging.info("STAGE 2: Cropping ROI with YOLO padding.....")
        
        crops_list = []
        
        padding = 10
        
        for box in xyxy:
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Add padding to avoid chipping away part of serial_zone
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image_array.shape[1], x2 + padding)
            y2 = min(image_array.shape[0], y2 + padding)
            
            # In Numpy, image data is stored under 3D array: [rows, columns, color channels]
            # By default, first index of this 3D array is row, then height & color channels
            # Thus, (y, x) format is being used for Numpy
            # y1:y2, x1:x2 = take the pixel region between y1 and y2 & x1 and x2
            crop = image_array[y1:y2, x1:x2]
            crops_list.append(crop)
        
        # ---------- STAGE 3: OCR Processing on YOLO-processed Cropped Image ----------
        logging.info("STAGE 3: Running EasyOCR for serial number extraction.....")
        
        detections = []
        
        # For loop: loop through multiple detected object per input image
        # Current setup will scaling in future if trained YOLO is required to detect more than one ROI (e.g: the date zone, prize type zone, etc..)
        # zip() will pair items from multiple iterables:
        # e.g:
        # xyxy = [[100, 50, 200, 120], [220, 80, 300, 140]]
        # confs = [0.95, 0.87]
        # cls_ids = [0, 2]
        # for (box, conf, cls_id) in zip(xyxy, confs, cls_ids):
        #   print(box, conf, cls_id)
        # Output:
        # [100, 50, 200, 120] 0.95 0
        # [220, 80, 300, 140] 0.87 2
        # enumerate() combine with for i (+ above) will yield the following:
        # i                 box                 conf            cls_id
        # 0         [100, 50, 200, 120]         0.95               0
        # 1         [220, 80, 300, 140]         0.87               2
        for i, (crop, conf, cls_id) in enumerate(zip(crops_list, confs, cls_ids)):
            
            # Skip low confidence detections
            if conf < MIN_CONFIDENCE:
                continue
        
            # Check Step: Determine if crop is present (since ROI of some input images is not always detected by YOLO)
            # If the crop is not present, it will be skipped - in this case, exit the pipeline as the current system only supporting 1 picture
            if (crop is None) or (crop.size == 0):
                logging.warning("Not able to detect the ROI of the input image!!!")
                continue
            
            # Running EasyOCR on cropped image after checking step
            try:
                # There are 3 value for 'detail' inside .readtext()
                # detail = 0: list[str], e.g: ["123456", "78934"]
                # detail = 1: list[tuple], e.g: [((bbox), text, confidence), ....]
                # detail = 2: dict, e.g: {'result': [...], 'image': [...],}
                # In this case, EasyOCR will return result as:
                # (Bounding box coordinates x1y1x2y2), (Recognize Text), (Confidence Score)
                ocr_result = reader.readtext(crop, detail = 1)
            
            except Exception as e:
                logging.error(f"Error: Can't performing extraction: {e}")
                ocr_result = []
                
            # Check Step: Determine if the cropped image from EasyOCR is successful
            if ocr_result:
                
                # In some case, EasyOCR could not detect a whole serial number but rather discrete parts and store them as different bounding boxes
                # Thus, " ".join will join all extracted info into a continuous string for later string manipulation
                combined_text = " ".join([text for (_, text, _) in ocr_result])
                
                # Similar reason to 'text' above
                # Thus, np.mean is used to compute the average mean
                avg_conf = float(np.mean([confidence for (_, _, confidence) in ocr_result]))
            
            # If the processed image is cropped unsuccessfully
            else:
                combined_text = ""
                avg_conf = 0.0
            
            # Perform string manipulation to extract only numbers from the 'combined_text' and omit any space / letter / ...
            digits = clean_text_digits(combined_text)
            
            # Extract crop dimensions for reference
            # .shape of any output from YOLO ROI detection will return 3 values: height, width, color channels
            crop_h, crop_w = crop.shape[:2]
            
            # Store necessary information under variable detection_result to display in terminal console
            detection_result = {
                "detection_id": i,
                "yolo_confidence": float(conf),
                "yolo_crop_region": {
                    "width": crop_w,
                    "height": crop_h
                },
                "ocr_raw_text": combined_text,
                "ocr_confidence": avg_conf,
                "extracted_digits": digits
            }
            
            detections.append(detection_result)
            logging.info(f"Detection {i}: Digits = {digits} (conf: {avg_conf:.2f})")
        
        return {
            "success": True,
            "detections": detections,
            "message": f"Successfully processed {len(detections)} detections"
        }
        
    except Exception as e:
        return {
            "success": False,
            "detections": [],
            "message": f"Error processing image: {str(e)}"      # Display error message to terminal console for debugging
        }