"""
Stream Processor for ANPR Camera Feeds
"""
import cv2
import threading
import time
import logging
import queue
from django.conf import settings
from .services import ANPRDetector

# Configure logger
logger = logging.getLogger('anpr_detection')

class StreamProcessor:
    """
    Process video streams from cameras for ANPR detection
    """
    def __init__(self, camera_obj):
        """
        Initialize stream processor for a camera
        
        Args:
            camera_obj: Camera model instance
        """
        self.camera = camera_obj
        self.rtsp_url = camera_obj.rtsp_url
        self.camera_id = camera_obj.id
        self.detector = ANPRDetector()
        self.is_running = False
        self.thread = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.detection_interval = 1.0  # Process every 1 second
        self.last_detection_time = 0
        
    def start(self):
        """Start processing the video stream"""
        if self.is_running:
            logger.warning(f"Stream processor for camera {self.camera.name} is already running")
            return False
            
        self.is_running = True
        self.thread = threading.Thread(target=self._process_stream)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Started stream processor for camera {self.camera.name}")
        return True
        
    def stop(self):
        """Stop processing the video stream"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None
        logger.info(f"Stopped stream processor for camera {self.camera.name}")
        
    def _process_stream(self):
        """Process the video stream in a separate thread"""
        # Open video capture
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video stream for camera {self.camera.name}")
            self.is_running = False
            return
            
        logger.info(f"Successfully opened video stream for camera {self.camera.name}")
        
        # Process frames
        while self.is_running:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Failed to read frame from camera {self.camera.name}")
                time.sleep(1.0)  # Wait before retry
                continue
                
            # Put frame in queue (non-blocking)
            try:
                self.frame_queue.put(frame, block=False)
            except queue.Full:
                # Queue is full, remove oldest frame
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame, block=False)
                except:
                    pass
                    
            # Process frames at regular intervals
            current_time = time.time()
            if current_time - self.last_detection_time >= self.detection_interval:
                self._process_detection(frame)
                self.last_detection_time = current_time
                
        # Release resources
        cap.release()
        
    def _process_detection(self, frame):
        """Process a frame for license plate detection"""
        try:
            # Process frame with ANPR detector
            result_frame, detections = self.detector.process_frame(frame, self.camera_id)
            
            # Save detections to database
            for detection_data in detections:
                self.detector.save_detection(detection_data, frame)
                
        except Exception as e:
            logger.error(f"Error processing detection for camera {self.camera.name}: {str(e)}")
            
    def get_latest_frame(self):
        """Get the latest processed frame with annotations"""
        try:
            # Get the latest frame from the queue without removing it
            latest_frame = self.frame_queue.queue[-1] if not self.frame_queue.empty() else None
            
            if latest_frame is not None:
                # Process the frame to add annotations
                result_frame, _ = self.detector.process_frame(latest_frame, self.camera_id)
                return result_frame
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting latest frame for camera {self.camera.name}: {str(e)}")
            return None


class StreamManager:
    """
    Manage multiple camera streams
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StreamManager, cls).__new__(cls)
            cls._instance.streams = {}
        return cls._instance
        
    def start_stream(self, camera_obj):
        """Start processing a camera stream"""
        camera_id = camera_obj.id
        
        # Check if stream is already running
        if camera_id in self.streams and self.streams[camera_id].is_running:
            logger.warning(f"Stream for camera {camera_obj.name} is already running")
            return False
            
        # Create and start stream processor
        processor = StreamProcessor(camera_obj)
        success = processor.start()
        
        if success:
            self.streams[camera_id] = processor
            
        return success
        
    def stop_stream(self, camera_id):
        """Stop processing a camera stream"""
        if camera_id in self.streams:
            self.streams[camera_id].stop()
            del self.streams[camera_id]
            return True
        return False
        
    def get_stream_frame(self, camera_id):
        """Get the latest frame from a camera stream"""
        if camera_id in self.streams:
            return self.streams[camera_id].get_latest_frame()
        return None
        
    def stop_all_streams(self):
        """Stop all camera streams"""
        for camera_id in list(self.streams.keys()):
            self.stop_stream(camera_id)