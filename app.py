from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import os
from PIL import ImageGrab
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)
CORS(app)

pyautogui.FAILSAFE = False

class HandGestureController:
    def __init__(self):
        print("\n" + "="*80)
        print("🌊 INITIALIZING WAVEX AI GESTURE SYSTEM")
        print("="*80 + "\n")
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=1
        )
        self.mp_draw = mp.solutions.drawing_utils
        print("✅ Hand detection: Ready")
        
        self.screen_w, self.screen_h = pyautogui.size()
        print(f"✅ Screen: {self.screen_w} x {self.screen_h}")
        
        self.cam_w, self.cam_h = 640, 480
        self.cap = None
        self.camera_running = False
        
        self.prev_x, self.prev_y = self.screen_w // 2, self.screen_h // 2
        self.smoothing = 5
        self.sensitivity = 60
        
        self.click_cd = 0
        self.screenshot_cd = 0
        self.slide_cd = 0
        
        self.scroll_prev_y = None
        self.last_gesture = "None"
        
        self.current_volume = 50
        self.current_brightness = 50
        
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.accuracy = 90
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.current_volume = int(self.volume.GetMasterVolumeLevelScalar() * 100)
            print(f"✅ Volume: {self.current_volume}%")
        except:
            self.volume = None
            print("⚠️  Volume: Using keyboard fallback")
        
        try:
            self.current_brightness = sbc.get_brightness()[0]
            print(f"✅ Brightness: {self.current_brightness}%")
        except:
            print("⚠️  Brightness: Run as Administrator")
        
        print("\n" + "="*80)
        print("✅ WAVEX READY!")
        print("="*80 + "\n")
    
    def init_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.cam_w)
            self.cap.set(4, self.cam_h)
            self.camera_running = True
    
    def stop_camera(self):
        if self.cap is not None:
            self.camera_running = False
            self.cap.release()
            self.cap = None
    
    def dist(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    
    def is_finger_up(self, lm, finger):
        if finger == "thumb":
            return lm[4][0] < lm[3][0]
        elif finger == "index":
            return lm[8][1] < lm[6][1]
        elif finger == "middle":
            return lm[12][1] < lm[10][1]
        elif finger == "ring":
            return lm[16][1] < lm[14][1]
        elif finger == "pinky":
            return lm[20][1] < lm[18][1]
        return False
    
    def count_fingers(self, lm):
        count = 0
        if self.is_finger_up(lm, "thumb"): count += 1
        if self.is_finger_up(lm, "index"): count += 1
        if self.is_finger_up(lm, "middle"): count += 1
        if self.is_finger_up(lm, "ring"): count += 1
        if self.is_finger_up(lm, "pinky"): count += 1
        return count
    
    def detect_gesture(self, lm):
        thumb_up = self.is_finger_up(lm, "thumb")
        index_up = self.is_finger_up(lm, "index")
        middle_up = self.is_finger_up(lm, "middle")
        ring_up = self.is_finger_up(lm, "ring")
        pinky_up = self.is_finger_up(lm, "pinky")
        
        finger_count = self.count_fingers(lm)
        thumb_index_dist = self.dist(lm[4], lm[8])
        
        if thumb_up and index_up and thumb_index_dist < 60:
            return "CLICK"
        if index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
            return "MOVE"
        if finger_count == 5:
            return "SCREENSHOT"
        if index_up and middle_up and not ring_up and not pinky_up and not thumb_up:
            return "SCROLL"
        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "NEXT_SLIDE"
        if pinky_up and not thumb_up and not index_up and not middle_up and not ring_up:
            return "PREV_SLIDE"
        if ring_up and not thumb_up and not index_up and not middle_up and not pinky_up:
            return "VOLUME"
        if index_up and middle_up and ring_up and not thumb_up and not pinky_up:
            return "BRIGHTNESS"
        return None
    
    def move_cursor(self, lm):
        x, y = lm[8]
        cam_margin_x, cam_margin_y = 100, 80
        
        screen_x = np.interp(x, [cam_margin_x, self.cam_w - cam_margin_x], [0, self.screen_w])
        screen_y = np.interp(y, [cam_margin_y, self.cam_h - cam_margin_y], [0, self.screen_h])
        
        screen_x = max(0, min(self.screen_w - 1, screen_x))
        screen_y = max(0, min(self.screen_h - 1, screen_y))
        
        smooth_x = self.prev_x + (screen_x - self.prev_x) / self.smoothing
        smooth_y = self.prev_y + (screen_y - self.prev_y) / self.smoothing
        
        pyautogui.moveTo(int(smooth_x), int(smooth_y))
        self.prev_x, self.prev_y = int(smooth_x), int(smooth_y)
    
    def click(self):
        if self.click_cd == 0:
            pyautogui.click()
            print("🖱️ CLICK!")
            self.click_cd = 8
    
    def screenshot(self):
        if self.screenshot_cd == 0:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{ts}.png"
            ImageGrab.grab().save(filename)
            print(f"📸 Screenshot: {os.path.abspath(filename)}")
            self.screenshot_cd = 30
    
    def scroll(self, lm):
        y = lm[12][1]
        if y < self.cam_h / 2:
            pyautogui.scroll(10)
        else:
            pyautogui.scroll(-10)
    
    def next_slide(self):
        if self.slide_cd == 0:
            pyautogui.press('right')
            print("➡️ NEXT SLIDE")
            self.slide_cd = 20
    
    def prev_slide(self):
        if self.slide_cd == 0:
            pyautogui.press('left')
            print("⬅️ PREV SLIDE")
            self.slide_cd = 20
    
    def volume_control(self, lm):
        x = lm[16][0]
        try:
            if x < self.cam_w * 0.4:
                if self.volume:
                    vol = self.volume.GetMasterVolumeLevelScalar()
                    new_vol = max(0.0, vol - 0.05)
                    self.volume.SetMasterVolumeLevelScalar(new_vol, None)
                    self.current_volume = int(new_vol * 100)
                else:
                    for _ in range(3):
                        pyautogui.press('volumedown')
                    self.current_volume = max(0, self.current_volume - 15)
                print(f"🔉 Volume: {self.current_volume}%")
            elif x > self.cam_w * 0.6:
                if self.volume:
                    vol = self.volume.GetMasterVolumeLevelScalar()
                    new_vol = min(1.0, vol + 0.05)
                    self.volume.SetMasterVolumeLevelScalar(new_vol, None)
                    self.current_volume = int(new_vol * 100)
                else:
                    for _ in range(3):
                        pyautogui.press('volumeup')
                    self.current_volume = min(100, self.current_volume + 15)
                print(f"🔊 Volume: {self.current_volume}%")
        except Exception as e:
            print(f"⚠️ Volume error: {e}")
    
    def brightness_control(self, lm):
        x = lm[12][0]
        try:
            current_br = sbc.get_brightness()[0]
            if x < self.cam_w / 2 - 50:
                new_br = max(0, current_br - 3)
                sbc.set_brightness(new_br)
                self.current_brightness = new_br
                print(f"🔅 Brightness: {new_br}%")
            elif x > self.cam_w / 2 + 50:
                new_br = min(100, current_br + 3)
                sbc.set_brightness(new_br)
                self.current_brightness = new_br
                print(f"💡 Brightness: {new_br}%")
        except Exception as e:
            print(f"⚠️ Brightness error: {e}")
    
    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        
        if self.click_cd > 0: self.click_cd -= 1
        if self.screenshot_cd > 0: self.screenshot_cd -= 1
        if self.slide_cd > 0: self.slide_cd -= 1
        
        gesture_text = "No Hand"
        
        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_lm, self.mp_hands.HAND_CONNECTIONS)
                
                lm = [(int(mark.x * self.cam_w), int(mark.y * self.cam_h)) 
                      for mark in hand_lm.landmark]
                
                gesture = self.detect_gesture(lm)
                
                if gesture == "MOVE":
                    self.move_cursor(lm)
                    gesture_text = "MOVE CURSOR"
                    self.last_gesture = "MOVE"
                elif gesture == "CLICK":
                    self.click()
                    gesture_text = "CLICKING!"
                    self.last_gesture = "CLICK"
                elif gesture == "SCREENSHOT":
                    self.screenshot()
                    gesture_text = "SCREENSHOT"
                    self.last_gesture = "SCREENSHOT"
                elif gesture == "SCROLL":
                    self.scroll(lm)
                    gesture_text = "SCROLL"
                    self.last_gesture = "SCROLL"
                elif gesture == "NEXT_SLIDE":
                    self.next_slide()
                    gesture_text = "NEXT SLIDE"
                    self.last_gesture = "NEXT_SLIDE"
                elif gesture == "PREV_SLIDE":
                    self.prev_slide()
                    gesture_text = "PREV SLIDE"
                    self.last_gesture = "PREV_SLIDE"
                elif gesture == "VOLUME":
                    self.volume_control(lm)
                    gesture_text = f"VOLUME: {self.current_volume}%"
                    self.last_gesture = "VOLUME"
                elif gesture == "BRIGHTNESS":
                    self.brightness_control(lm)
                    gesture_text = f"BRIGHTNESS: {self.current_brightness}%"
                    self.last_gesture = "BRIGHTNESS"
        else:
            self.last_gesture = "None"
        
        cv2.putText(frame, gesture_text, (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        self.frame_count += 1
        if time.time() - self.fps_start_time > 1:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_start_time = time.time()
        
        return frame
    
    def get_frame(self):
        if not self.camera_running or self.cap is None:
            return None
        success, frame = self.cap.read()
        if not success:
            return None
        frame = self.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def get_stats(self):
        return {
            "gesture": self.last_gesture,
            "fps": self.fps,
            "accuracy": self.accuracy,
            "volume": self.current_volume,
            "brightness": self.current_brightness
        }

controller = HandGestureController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        controller.init_camera()
        while controller.camera_running:
            frame = controller.get_frame()
            if frame is None:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        controller.stop_camera()
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    return jsonify(controller.get_stats())

@app.route('/settings', methods=['POST'])
def settings():
    data = request.json
    if 'smoothing' in data:
        controller.smoothing = max(1, min(20, int(data['smoothing'])))
    if 'sensitivity' in data:
        controller.sensitivity = int(data['sensitivity'])
    return jsonify({"status": "ok"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    controller.stop_camera()
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    print("\n🌊 WAVEX AI SERVER STARTING")
    print(f"🌐 Open: http://localhost:5000\n")
    app.run(debug=False, host='0.0.0.0', port=5000)