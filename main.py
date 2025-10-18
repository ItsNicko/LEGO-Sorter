import cv2
import threading
import tflite_runtime.interpreter as tflite
import serial
import time

# -------------------------
# UART setup
# -------------------------
SERIAL_PORT = "/dev/ttyS1"  # Orange Pi UART port
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def send_command(cmd: str):
    """Send a command string to Cortex over UART"""
    ser.write((cmd + "\n").encode())
    print(f"Sent command: {cmd}")

# -------------------------
# Load TensorFlow Lite models
# -------------------------
color_model = tflite.Interpreter(model_path="color_model.tflite")
shape_model = tflite.Interpreter(model_path="shape_model.tflite")
color_model.allocate_tensors()
shape_model.allocate_tensors()

# -------------------------
# Helper function to run inference
# -------------------------
def run_inference(interpreter, frame):
    # Resize frame to model input size
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    img = cv2.resize(frame, (width, height))
    img = img.astype('float32')
    img = img / 255.0
    img = img.reshape(input_details[0]['shape'])

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    return output

# -------------------------
# Shared frame
# -------------------------
frame_global = None
lock = threading.Lock()

# -------------------------
# Color detection thread
# -------------------------
color_result = None
def color_thread():
    global color_result
    while True:
        if frame_global is not None:
            with lock:
                result = run_inference(color_model, frame_global)
            color_result = result
            # print("Color result:", result)

# -------------------------
# Shape detection thread
# -------------------------
shape_result = None
def shape_thread():
    global shape_result
    while True:
        if frame_global is not None:
            with lock:
                result = run_inference(shape_model, frame_global)
            shape_result = result
            # print("Shape result:", result)

# -------------------------
# Start threads
# -------------------------
threading.Thread(target=color_thread, daemon=True).start()
threading.Thread(target=shape_thread, daemon=True).start()

# -------------------------
# Camera capture
# -------------------------
cap = cv2.VideoCapture(0)  # default camera

# -------------------------
# Conveyor logic
# -------------------------
def piece_detected(color_result, shape_result):
    """
    Define your detection logic based on model outputs
    Return True if a piece is detected that needs sorting
    """
    # Placeholder: replace with your own thresholds
    if color_result is not None and shape_result is not None:
        color_confidence = color_result[0][0]  # example
        shape_confidence = shape_result[0][0]  # example
        if color_confidence > 0.5 or shape_confidence > 0.5:
            return True
    return False

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Update global frame for threads
    with lock:
        frame_global = frame.copy()

    # Run piece detection logic
    if piece_detected(color_result, shape_result):
        # Stop conveyor
        send_command("M2_STOP")
        # Rotate bucket
        send_command("M1_CW90")
        # Wait for bucket rotation to finish
        time.sleep(1)  # match Cortex motor timing
        # Resume conveyor
        send_command("M2_START")
        # Small delay to avoid double detection
        time.sleep(0.5)
