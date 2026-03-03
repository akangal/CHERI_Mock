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

# --- 4. EXECUTE TEST ---
try:
    print("\n--- TEST START ---")
    
    # FORWARD
    print("Moving FORWARD...")
    set_all_speed(60000) # ~90% speed
    for i in range(1, 5):
        set_motor(i, "FORWARD")
    time.sleep(3)
    
    # STOP
    print("STOPPING...")
    set_all_speed(0)
    for i in range(1, 5):
        set_motor(i, "RELEASE")
    time.sleep(1)
    
    # BACKWARD
    print("Moving BACKWARD...")
    set_all_speed(60000)
    for i in range(1, 5):
        set_motor(i, "BACKWARD")
    time.sleep(3)
    
finally:
    # Always turn everything off when the script ends or is interrupted
    print("\nSecuring hardware...")
    set_all_speed(0)
    for i in range(1, 5):
        set_motor(i, "RELEASE")
    MOTOR_ENABLE.value(1)
    print("Test Complete.")