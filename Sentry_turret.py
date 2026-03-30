import cv2
import time
from pyfirmata import Arduino, util

# === Arduino Setup ===
board = Arduino('COM8')  # Change as needed

servo_x_pin = board.get_pin('d:9:s')
servo_y_pin = board.get_pin('d:10:s')
servo_trigger_pin = board.get_pin('d:11:s')

# Initial positions
angle_x = 90
angle_y = 60
trigger_default = 180
trigger_active = 0

servo_x_pin.write(angle_x)
servo_y_pin.write(angle_y)
servo_trigger_pin.write(trigger_default)
time.sleep(1)

# === Load DNN Face Detector ===
modelFile = "res10_300x300_ssd_iter_140000.caffemodel"
configFile = "deploy.prototxt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

cap = cv2.VideoCapture(0)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
center_x = frame_width // 2
center_y = frame_height // 2

# === Settings ===
tolerance = 40
move_step = 3
servo_speed = 0.005  # <-- Lower = faster, e.g., try 0.002 for fast, 0.01 for slow
trigger_cooldown = 2
trigger_active_delay = 0.5
last_trigger_time = 0

def smooth_servo_move(servo_pin, current_angle, target_angle, delay):
    step = 1 if target_angle > current_angle else -1
    for angle in range(int(current_angle), int(target_angle), step):
        servo_pin.write(angle)
        time.sleep(delay)
    servo_pin.write(target_angle)

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # === Face Detection ===
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    face_centered = False
    closest_face = None
    min_dist = float('inf')

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6:
            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            (x1, y1, x2, y2) = box.astype("int")
            face_x = (x1 + x2) // 2
            face_y = (y1 + y2) // 2
            dist = ((face_x - center_x) ** 2 + (face_y - center_y) ** 2) ** 0.5

            if dist < min_dist:
                min_dist = dist
                closest_face = (x1, y1, x2, y2)

    if closest_face:
        x1, y1, x2, y2 = closest_face
        face_x = (x1 + x2) // 2
        face_y = (y1 + y2) // 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Horizontal
        if face_x < center_x - tolerance:
            new_x = min(180, angle_x + move_step)
            smooth_servo_move(servo_x_pin, angle_x, new_x, servo_speed)
            angle_x = new_x
        elif face_x > center_x + tolerance:
            new_x = max(0, angle_x - move_step)
            smooth_servo_move(servo_x_pin, angle_x, new_x, servo_speed)
            angle_x = new_x

        # Vertical (inverted)
        if face_y < center_y - tolerance:
            new_y = max(0, angle_y - move_step)
            smooth_servo_move(servo_y_pin, angle_y, new_y, servo_speed)
            angle_y = new_y
        elif face_y > center_y + tolerance:
            new_y = min(180, angle_y + move_step)
            smooth_servo_move(servo_y_pin, angle_y, new_y, servo_speed)
            angle_y = new_y

        # Center check
        if abs(face_x - center_x) <= tolerance and abs(face_y - center_y) <= tolerance:
            face_centered = True

    # === Trigger Servo (unchanged) ===
    current_time = time.time()
    if face_centered and (current_time - last_trigger_time > trigger_cooldown):
        servo_trigger_pin.write(trigger_active)
        time.sleep(trigger_active_delay)
        servo_trigger_pin.write(trigger_default)
        last_trigger_time = time.time()

    cv2.imshow("DNN Face Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
board.exit()
