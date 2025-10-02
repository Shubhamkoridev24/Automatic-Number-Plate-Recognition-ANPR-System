"""
ANPR Detection Services
"""
import os
import cv2
import numpy as np
import logging
import pytesseract
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from anpr_cameras.models import Camera
from anpr_alerts.models import Blacklist, Alert
from .models import Detection

# Configure logger
logger = logging.getLogger('anpr_detection')

class ANPRDetector:
    """
    Automatic Number Plate Recognition detector using YOLO and Tesseract OCR
    """
    def __init__(self, mock_mode=True):
        """
        Initialize ANPR detector
        
        Args:
            mock_mode: If True, use mock detection instead of actual models
        """
        self.mock_mode = mock_mode
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        
        # Initialize YOLO model if not in mock mode
        if not mock_mode:
            try:
                # Path to YOLO model files
                model_dir = os.path.join(settings.BASE_DIR, 'anpr_detection', 'ml_models')
                weights_path = os.path.join(model_dir, 'yolov4-plate.weights')
                config_path = os.path.join(model_dir, 'yolov4-plate.cfg')
                
                # Check if model files exist
                if os.path.exists(weights_path) and os.path.exists(config_path):
                    self.net = cv2.dnn.readNet(weights_path, config_path)
                    self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                    self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                    logger.info("YOLO model loaded successfully")
                else:
                    logger.warning("YOLO model files not found, using mock mode")
                    self.mock_mode = True
            except Exception as e:
                logger.error(f"Error loading YOLO model: {str(e)}")
                self.mock_mode = True
        
    def detect_plates(self, image):
        """
        Detect license plates in an image using YOLO
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            List of detected plate regions (x, y, w, h, confidence)
        """
        if self.mock_mode:
            # Mock detection - return a fake plate in the center of the image
            h, w = image.shape[:2]
            plate_w = int(w * 0.2)
            plate_h = int(h * 0.1)
            x = int((w - plate_w) / 2)
            y = int((h - plate_h) / 2)
            return [(x, y, plate_w, plate_h, 0.95)]
            
        try:
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Create blob from image
            blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
            
            # Set input and get output
            self.net.setInput(blob)
            output_layers = self.net.getUnconnectedOutLayersNames()
            layer_outputs = self.net.forward(output_layers)
            
            # Process outputs
            boxes = []
            confidences = []
            
            for output in layer_outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > self.confidence_threshold:
                        # Scale bounding box coordinates back to original image size
                        box = detection[0:4] * np.array([width, height, width, height])
                        center_x, center_y, box_width, box_height = box.astype("int")
                        
                        # Get top-left corner coordinates
                        x = int(center_x - (box_width / 2))
                        y = int(center_y - (box_height / 2))
                        
                        boxes.append((x, y, int(box_width), int(box_height)))
                        confidences.append(float(confidence))
            
            # Apply non-maximum suppression
            indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
            
            # Get final detections
            detections = []
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, w, h = boxes[i]
                    confidence = confidences[i]
                    detections.append((x, y, w, h, confidence))
                    
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting plates: {str(e)}")
            return []
    
    def recognize_text(self, plate_img):
        """
        Recognize text on license plate using Tesseract OCR
        
        Args:
            plate_img: Cropped license plate image
            
        Returns:
            Recognized text and confidence
        """
        if self.mock_mode:
            # Mock OCR - return a fake plate number
            import random
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            numbers = "0123456789"
            plate = ''.join(random.choice(letters) for _ in range(2))
            plate += ''.join(random.choice(numbers) for _ in range(2))
            plate += ''.join(random.choice(letters) for _ in range(2))
            return plate, 0.9
            
        try:
            # Preprocess image for OCR
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply OCR
            config = '--psm 7 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            text = pytesseract.image_to_string(thresh, config=config).strip()
            
            # Get confidence
            data = pytesseract.image_to_data(thresh, config=config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            confidence = sum(confidences) / len(confidences) if confidences else 0
            confidence = confidence / 100.0  # Convert to 0-1 range
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"Error recognizing text: {str(e)}")
            return "", 0.0
    
    def process_frame(self, frame, camera_id=None):
        """
        Process a video frame for license plate detection and recognition
        
        Args:
            frame: Input video frame
            camera_id: Optional camera ID
            
        Returns:
            Annotated frame and list of detections
        """
        # Make a copy of the frame for annotations
        result_frame = frame.copy()
        
        # Detect license plates
        plate_detections = self.detect_plates(frame)
        
        # Process each detection
        detections = []
        for (x, y, w, h, confidence) in plate_detections:
            # Extract plate region
            plate_img = frame[max(0, y):min(y+h, frame.shape[0]), max(0, x):min(x+w, frame.shape[1])]
            
            if plate_img.size == 0:
                continue
                
            # Recognize text
            plate_number, ocr_confidence = self.recognize_text(plate_img)
            
            # Skip if no text recognized
            if not plate_number:
                continue
                
            # Calculate final confidence
            final_confidence = confidence * ocr_confidence
            
            # Check if plate is in blacklist
            is_blacklisted = self._check_blacklist(plate_number)
            
            # Add to detections
            detections.append({
                'plate_number': plate_number,
                'confidence': final_confidence,
                'box': (x, y, w, h),
                'is_blacklisted': is_blacklisted,
                'camera_id': camera_id
            })
            
            # Draw bounding box
            color = (0, 0, 255) if is_blacklisted else (0, 255, 0)
            cv2.rectangle(result_frame, (x, y), (x+w, y+h), color, 2)
            
            # Draw text
            text = f"{plate_number} ({final_confidence:.2f})"
            cv2.putText(result_frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        return result_frame, detections
    
    def save_detection(self, detection_data, frame):
        """
        Save detection to database
        
        Args:
            detection_data: Detection data dictionary
            frame: Original frame
            
        Returns:
            Detection object or None if failed
        """
        try:
            # Extract data
            plate_number = detection_data['plate_number']
            confidence = detection_data['confidence']
            camera_id = detection_data['camera_id']
            is_blacklisted = detection_data['is_blacklisted']
            x, y, w, h = detection_data['box']
            
            # Skip if no camera ID
            if not camera_id:
                return None
                
            # Get camera
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                logger.error(f"Camera with ID {camera_id} does not exist")
                return None
                
            # Save image
            now = timezone.now()
            date_str = now.strftime("%Y%m%d_%H%M%S")
            img_dir = os.path.join(settings.MEDIA_ROOT, 'detections')
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, f"{plate_number}_{date_str}.jpg")
            rel_path = os.path.join('detections', f"{plate_number}_{date_str}.jpg")
            cv2.imwrite(img_path, frame)
            
            # Create detection
            detection = Detection.objects.create(
                plate_number=plate_number,
                camera=camera,
                confidence=confidence,
                is_blacklisted=is_blacklisted,
                image_path=rel_path,
                processed=False
            )
            
            # Create alert if blacklisted
            if is_blacklisted:
                self._create_alert(detection)
                
            logger.info(f"Saved detection: {plate_number} (Camera: {camera.name})")
            return detection
            
        except Exception as e:
            logger.error(f"Error saving detection: {str(e)}")
            return None
    
    def _check_blacklist(self, plate_number):
        """
        Check if a plate number is in the blacklist
        
        Args:
            plate_number: License plate number
            
        Returns:
            True if blacklisted, False otherwise
        """
        try:
            return Blacklist.objects.filter(plate_number=plate_number, is_active=True).exists()
        except Exception as e:
            logger.error(f"Error checking blacklist: {str(e)}")
            return False
    
    def _create_alert(self, detection):
        """
        Create an alert for a blacklisted detection
        
        Args:
            detection: Detection object
        """
        try:
            # Get blacklist entry
            blacklist = Blacklist.objects.filter(plate_number=detection.plate_number, is_active=True).first()
            
            if blacklist:
                # Create alert
                Alert.objects.create(
                    detection=detection,
                    blacklist=blacklist,
                    notified=False
                )
                logger.info(f"Created alert for blacklisted plate: {detection.plate_number}")
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")