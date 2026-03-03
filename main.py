import network
import socket
import time
from machine import Pin, PWM

# --- 1. PIN CONFIGURATION ---
pwm_pins = {
    1: PWM(Pin(5)),   # M1
    2: PWM(Pin(13)),  # M2
    3: PWM(Pin(11)),  # M3
    4: PWM(Pin(10))   # M4
}

MOTOR_LATCH  = Pin(4, Pin.OUT)
MOTOR_CLK    = Pin(12, Pin.OUT)
MOTOR_DATA   = Pin(7, Pin.OUT)
MOTOR_ENABLE = Pin(9, Pin.OUT)

# --- 2. ANTI-JITTER BOOT SEQUENCE ---
print("Running Clean Boot Sequence...")
MOTOR_ENABLE.value(1) # Disable output first

# Set to 7.6 kHz to match your C++ code and 0 speed
for p in pwm_pins.values():
    p.freq(7600) 
    p.duty_u16(0)

# Flush the shift register with zeros (with micro-delays for stability)
MOTOR_LATCH.value(0)
time.sleep_us(10)
for _ in range(8):
    MOTOR_CLK.value(0)
    MOTOR_DATA.value(0)
    time.sleep_us(10)
    MOTOR_CLK.value(1)
    time.sleep_us(10)
MOTOR_LATCH.value(1)
time.sleep_us(10)

# Safely enable chips
MOTOR_ENABLE.value(0)

# --- 3. MOTOR LOGIC ---
MOTOR_BITS = {
    '1A': 2, '1B': 3, '2A': 1, '2B': 4,
    '3A': 5, '3B': 7, '4A': 0, '4B': 6
}
current_latch_state = 0

def update_shift_register():
    MOTOR_LATCH.value(0)
    time.sleep_us(10)
    for i in range(7, -1, -1):
        MOTOR_CLK.value(0)
        bit = (current_latch_state >> i) & 1
        MOTOR_DATA.value(bit)
        time.sleep_us(10)
        MOTOR_CLK.value(1)
        time.sleep_us(10)
    MOTOR_LATCH.value(1)
    time.sleep_us(10)

def set_motor(motor_id, mode):
    global current_latch_state
    a_bit = MOTOR_BITS[f'{motor_id}A']
    b_bit = MOTOR_BITS[f'{motor_id}B']
    
    # *** DIRECTIONS REVERSED HERE ***
    if mode == "FORWARD":
        current_latch_state &= ~(1 << a_bit)
        current_latch_state |= (1 << b_bit)
    elif mode == "BACKWARD":
        current_latch_state |= (1 << a_bit)
        current_latch_state &= ~(1 << b_bit)
    elif mode == "RELEASE":
        current_latch_state &= ~(1 << a_bit)
        current_latch_state &= ~(1 << b_bit)
    
    update_shift_register()

def set_all_speed(duty):
    for p in pwm_pins.values():
        p.duty_u16(duty)

# --- 4. ROBOT MOVEMENT WRAPPER (Using YOUR exact working sequence) ---
def robot_move(command):
    if command == "forward":
        set_all_speed(60000)
        for i in range(1, 5): set_motor(i, "FORWARD")
    elif command == "backward":
        set_all_speed(60000)
        for i in range(1, 5): set_motor(i, "BACKWARD")
    elif command == "left":
        # Assumes M1/M3 are Left, M2/M4 are Right. 
        set_all_speed(60000)
        set_motor(1, "BACKWARD"); set_motor(3, "BACKWARD")
        set_motor(2, "FORWARD"); set_motor(4, "FORWARD")
    elif command == "right":
        set_all_speed(60000)
        set_motor(1, "FORWARD"); set_motor(3, "FORWARD")
        set_motor(2, "BACKWARD"); set_motor(4, "BACKWARD")
    elif command == "stop":
        set_all_speed(0)
        for i in range(1, 5): set_motor(i, "RELEASE")

# Start dead stop
robot_move("stop")

# --- 5. WIFI & WEB SERVER ---
print("Starting Wi-Fi Access Point...")
ap = network.WLAN(network.AP_IF)
ap.config(essid='Cheri Mock', password='metu2026')
ap.active(True)

while not ap.active():
    time.sleep(1)

print("Wi-Fi Active! IP:", ap.ifconfig()[0])

# --- WEB SERVER ---
html = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>button{width:90px;height:90px;margin:10px;font-size:18px;background:#eee;border-radius:10px;}</style></head>
<body style="text-align:center; font-family: sans-serif;">
    <h1>CHERI MOCK Control</h1>
    <button onclick="fetch('/forward')">FORWARD</button><br>
    <button onclick="fetch('/left')">LEFT</button>
    <button onclick="fetch('/stop')" style="background:#ffcccc">STOP</button>
    <button onclick="fetch('/right')">RIGHT</button><br>
    <button onclick="fetch('/backward')">BACKWARD</button>
</body></html>"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

print("CHERI Web Server Ready! Connect phone to 'Cheri Mock' and open http://192.168.4.1")

try:
    while True:
        client, addr = s.accept()
        request = client.recv(1024).decode()
        
        try:
            path = request.split(' ')[1][1:] 
            if path in ['forward', 'backward', 'left', 'right', 'stop']:
                robot_move(path)
                print(f"Executing: {path}")
        except Exception as e:
            pass
            
        client.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n' + html)
        client.close()
finally:
    print("Shutting down safely...")
    robot_move("stop")
    MOTOR_ENABLE.value(1)
