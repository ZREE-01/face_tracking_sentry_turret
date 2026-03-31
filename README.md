# face_tracking_sentry_turret
A real-time face tracking sentry turret using OpenCV on PC and Arduino for servo control.
## How it works
The Sentry turret uses a USB webcam connected to a PC. The PC runs a Python script using OpenCV to detect faces. When a face is detected, the script calculates the horizontal and vertical offsets of the face from the center of the frame and maps the servo angles and adjusts three servo motors using arduino(via StandardFirmata), one for pan, one for tilt, and one for trigger, to keep the turret pointing at the detected face, and triggers the turret when the face is centered.
## Components
- Arduino UNO (running StandardFirmata)
- 2x MG995 Servo Motor
- 1x 9g Servo Motor
- USB Webcam
- PC (running OpenCV)
- Turret frame
## Software Component
- Python3 - running OpenCV and PyFirmata
## Data flow chart
Webcam -> PC(OpenCV + PyFirmata) -> USB -> Arduino(StandardFirmata) -> Servos
## Code
[Sentry_turret.py](Sentry_turret.py)

--
Built independently as a part of a Robotics and Electronics learning journey.
