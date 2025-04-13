import cv2
import mediapipe as mp
import pyautogui
import speech_recognition as sr
import threading
import time
import math
import numpy as np
import subprocess
import os

# Disable PyAutoGUI fail-safe (optional but helpful)
pyautogui.FAILSAFE = False

# Screen size
screen_width, screen_height = pyautogui.size()

# Feature flags
tracking_enabled = True
blink_control_enabled = True
keyboard_enabled = False
exit_app = False

# UI Button Coordinates
button_coords_tracking = (10, 10, 160, 60)
button_coords_blink = (180, 10, 340, 60)
button_coords_keyboard = (360, 10, 520, 60)

# Eye aspect ratio constants
LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]
EAR_THRESHOLD = 0.21
CONSEC_FRAMES = 2

# Sensitivity for head tracking
sensitivity = 3.5

def calculate_ear(landmarks, eye_indices):
    def euclidean(p1, p2):
        return math.dist([p1.x, p1.y], [p2.x, p2.y])
    top = euclidean(landmarks[eye_indices[1]], landmarks[eye_indices[5]]) + \
          euclidean(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    bottom = 2.0 * euclidean(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    return top / bottom

def open_on_screen_keyboard():
    try:
        subprocess.Popen('osk.exe', shell=True)
        print("On-Screen Keyboard Opened")
    except Exception as e:
        print("Failed to open on-screen keyboard:", str(e))

def close_on_screen_keyboard():
    try:
        os.system('taskkill /f /im osk.exe')
        print("On-Screen Keyboard Closed")
    except Exception as e:
        print("Failed to close on-screen keyboard:", str(e))

def click_event(event, x, y, flags, param):
    global tracking_enabled, blink_control_enabled, keyboard_enabled
    if event == cv2.EVENT_LBUTTONDOWN:
        if button_coords_tracking[0] <= x <= button_coords_tracking[2] and button_coords_tracking[1] <= y <= button_coords_tracking[3]:
            tracking_enabled = not tracking_enabled
        elif button_coords_blink[0] <= x <= button_coords_blink[2] and button_coords_blink[1] <= y <= button_coords_blink[3]:
            blink_control_enabled = not blink_control_enabled
        elif button_coords_keyboard[0] <= x <= button_coords_keyboard[2] and button_coords_keyboard[1] <= y <= button_coords_keyboard[3]:
            keyboard_enabled = not keyboard_enabled
            if keyboard_enabled:
                open_on_screen_keyboard()
            else:
                close_on_screen_keyboard()

def blink_action_tracker(blinks_in_duration):
    while not exit_app:
        current_time = time.time()
        for duration, required_blinks, action in [(3, 2, 'click'), (4, 3, 'doubleClick'), (5, 4, 'rightClick')]:
            valid_blinks = [t for t in blinks_in_duration if current_time - t <= duration]
            if len(valid_blinks) >= required_blinks:
                print(f"Triggering: {action}")
                if action == "click":
                    pyautogui.click()
                elif action == "doubleClick":
                    pyautogui.doubleClick()
                elif action == "rightClick":
                    pyautogui.rightClick()
                blinks_in_duration.clear()
        time.sleep(1)

def head_tracking():
    global tracking_enabled, blink_control_enabled, keyboard_enabled, exit_app

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # More stable on Windows

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Cannot access webcam.")
        exit_app = True
        return

    cv2.startWindowThread()
    cv2.namedWindow("Head Tracking")
    cv2.setMouseCallback("Head Tracking", click_event)

    blink_counter = 0
    frame_counter = 0
    blinks_in_duration = []

    threading.Thread(target=blink_action_tracker, args=(blinks_in_duration,), daemon=True).start()

    with mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:

        while cap.isOpened() and not exit_app:
            try:
                success, frame = cap.read()
                if not success:
                    print("Failed to read frame from webcam.")
                    continue

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = face_mesh.process(rgb_frame)

                if result.multi_face_landmarks:
                    landmarks = result.multi_face_landmarks[0].landmark

                    if len(landmarks) > 1:
                        nose = landmarks[1]

                        x_offset = (nose.x - 0.5) * sensitivity
                        y_offset = (nose.y - 0.5) * sensitivity
                        x = int((0.5 + x_offset) * screen_width)
                        y = int((0.5 + y_offset) * screen_height)
                        x = max(0, min(screen_width - 1, x))
                        y = max(0, min(screen_height - 1, y))

                        if tracking_enabled:
                            pyautogui.moveTo(x, y)

                        if blink_control_enabled:
                            left_ear = calculate_ear(landmarks, LEFT_EYE_IDX)
                            right_ear = calculate_ear(landmarks, RIGHT_EYE_IDX)
                            ear = (left_ear + right_ear) / 2.0

                            if ear < EAR_THRESHOLD:
                                frame_counter += 1
                            else:
                                if frame_counter >= CONSEC_FRAMES:
                                    blink_counter += 1
                                    blinks_in_duration.append(time.time())
                                    print("Blink detected")
                                frame_counter = 0

                # Draw UI buttons
                buttons = [
                    (button_coords_tracking, "Tracking", tracking_enabled),
                    (button_coords_blink, "Blink Ctrl", blink_control_enabled),
                    (button_coords_keyboard, "Keyboard", keyboard_enabled)
                ]
                for coords, label, state in buttons:
                    color = (0, 255, 0) if state else (0, 0, 255)
                    cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), color, -1)
                    cv2.putText(frame, f"{'On' if state else 'Off'} {label}", (coords[0]+5, coords[1]+35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.imshow("Head Tracking", frame)

                if cv2.waitKey(1) == 27:
                    exit_app = True
                    break

                time.sleep(0.01)  # Prevent CPU overuse

            except Exception as e:
                print("Error in head_tracking loop:", str(e))
                continue

    cap.release()
    cv2.destroyAllWindows()

def voice_commands():
    global exit_app
    recognizer = sr.Recognizer()

    while not exit_app:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for voice command...")
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print("You said:", command)

                if "click" in command and "double" not in command and "hold" not in command:
                    pyautogui.click()
                elif "double click" in command:
                    pyautogui.doubleClick()
                elif "option menu" in command or "right click" in command:
                    pyautogui.rightClick()
                elif "hold click" in command:
                    pyautogui.mouseDown()
                elif "release click" in command:
                    pyautogui.mouseUp()

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Speech recognition service error.")
        except Exception as e:
            print("Voice Command Error:", str(e))

if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=head_tracking)
        t2 = threading.Thread(target=voice_commands)

        t1.start()
        t2.start()

        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("Exiting...")
        exit_app = True
