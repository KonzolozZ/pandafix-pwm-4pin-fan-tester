from machine import Pin, PWM, I2C, Timer, reset
from ssd1306 import SSD1306_I2C
import utime
import gc

# ========== HARDVER KONFIGURÁCIÓ ==========
PWM_PIN = 16      # PWM kimenet ventilátorhoz
TACH_PIN = 17     # TACH bemenet fordulatszám méréshez
BTN_MENU = 14     # Menü gomb
BTN_SELECT = 15   # Kiválasztás gomb
I2C_SCL = 5       # OLED SCL
I2C_SDA = 4       # OLED SDA

# OLED beállítások
OLED_WIDTH = 128
OLED_HEIGHT = 32

# PWM beállítások
PWM_FREQ = 25000  # 25kHz - csendes működés
PWM_STEPS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Sebességi lépések %

# Időzítések
SPLASH_TIME = 5000    # 5 másodperc splash screen
AUTO_STEP_TIME = 8000 # 2 másodperc automatikus módban
DEBOUNCE_TIME = 200   # Gomb debounce idő ms
RPM_MEASURE_INTERVAL = 1000  # RPM mérés gyakorisága ms

print("Pandafix - Fan Tester inicializálása...")

# ========== HARDVER INICIALIZÁLÁS ==========
try:
    # I2C és OLED
    i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400000)
    print("I2C eszközök:", i2c.scan())
    
    # OLED
    oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
    print("OLED inicializálva")
    
    # PWM
    pwm = PWM(Pin(PWM_PIN))
    pwm.freq(PWM_FREQ)
    pwm.duty_u16(0)
    print("PWM inicializálva")
    
    # TACH pin
    tach_pin = Pin(TACH_PIN, Pin.IN, Pin.PULL_UP)
    print("TACH pin inicializálva")
    
    # Gombok
    btn_menu = Pin(BTN_MENU, Pin.IN, Pin.PULL_UP)
    btn_select = Pin(BTN_SELECT, Pin.IN, Pin.PULL_UP)
    print("Gombok inicializálva")
    
except Exception as e:
    print("Hardver inicializálási hiba:", e)
    while True:
        pass

# ========== GLOBÁLIS VÁLTOZÓK ==========
# Menü állapotok
menu_items = ["AUTO", "MANUAL"]
current_menu = 0
in_menu = True
current_mode = None  # "auto" vagy "manual"

# Ventilátor állapot
current_speed_index = 0
current_speed_percent = PWM_STEPS[0]

# TACH/RPM
tach_count = 0
current_rpm = 0
last_rpm_measure = 0

# Gomb kezelés
last_menu_press = 0
last_select_press = 0

# Animáció
animation_frame = 0
last_animation_update = 0
ANIMATION_SPEED = 300  # ms

# Auto mód
last_auto_step = 0

# ========== ANIMÁLT VENTILÁTOR IKON ==========
fan_frames = [
    [
        0b00011000,
        0b00111100,
        0b01111110,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000
    ],
    [
        0b00100100,
        0b01000010,
        0b10111101,
        0b11111111,
        0b11111111,
        0b10111101,
        0b01000010,
        0b00100100
    ],
    [
        0b00011000,
        0b00111100,
        0b01111110,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000
    ],
    [
        0b01000010,
        0b00100100,
        0b10111101,
        0b11111111,
        0b11111111,
        0b10111101,
        0b00100100,
        0b01000010
    ]
]

# ========== SEGÉDFÜGGVÉNYEK ==========
def tach_interrupt(pin):
    """TACH interrupt kezelő"""
    global tach_count
    tach_count += 1

# TACH interrupt bekapcsolása
tach_pin.irq(trigger=Pin.IRQ_FALLING, handler=tach_interrupt)

def calculate_rpm():
    """RPM számítás"""
    global tach_count, current_rpm
    
    # A legtöbb 4-pin ventilátor 2 impulzust ad fordulatonként
    rpm = (tach_count * 30)  # 30 = 60 / 2
    current_rpm = rpm
    tach_count = 0
    return rpm

def set_fan_speed(percent):
    """Ventilátor sebesség beállítása"""
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    
    duty = int((percent / 100.0) * 65535)
    pwm.duty_u16(duty)
    return percent

def draw_fan_icon(x, y, frame):
    """Animált ventilátor ikon rajzolása"""
    if frame >= len(fan_frames):
        frame = 0
    
    bitmap = fan_frames[frame]
    
    for row in range(8):
        for col in range(8):
            if (bitmap[row] >> (7 - col)) & 1:
                if x + col < OLED_WIDTH and y + row < OLED_HEIGHT:
                    oled.pixel(x + col, y + row, 1)

def debounce_button(button, last_press_time):
    """Gomb debounce"""
    current_time = utime.ticks_ms()
    if button.value() == 0 and utime.ticks_diff(current_time, last_press_time) > DEBOUNCE_TIME:
        return True, current_time
    return False, last_press_time

def show_splash_screen():
    """Kezdő képernyő megjelenítése"""
    try:
        oled.fill(0)
        oled.text("Pandafix", 30, 5, 1)
        oled.text("Fan Tester", 25, 20, 1)
        oled.show()
        print("Splash screen megjelenítve")
        utime.sleep_ms(SPLASH_TIME)
    except Exception as e:
        print("Splash screen hiba:", e)

def show_menu():
    """Horizontális menü megjelenítése"""
    try:
        oled.fill(0)
        
        # Címsor
        oled.text("SELECT MODE", 14, 0, 1)
        
        # Aktuális menüelem
        item = menu_items[current_menu]
        text_width = len(item) * 8
        x_pos = (OLED_WIDTH - text_width) // 2
        
        # Bal nyíl
        oled.text("<", 2, 16, 1)
        
        # Menüelem
        oled.text(item, x_pos, 16, 1)
        
        # Jobb nyíl
        oled.text(">", OLED_WIDTH - 10, 16, 1)
        
        oled.show()
    except Exception as e:
        print("Menü megjelenítési hiba:", e)

def show_status_screen():
    """Státusz képernyő"""
    global animation_frame, last_animation_update
    
    try:
        oled.fill(0)
        
        # Fejléc
        mode_text = "AUTO TEST" if current_mode == "auto" else "MANUAL TEST"
        oled.text(mode_text, 0, 0, 1)
        
        # PWM és RPM
        oled.text("PWM:{}%".format(current_speed_percent), 0, 8, 1)
        oled.text("RPM:{}".format(current_rpm), 0, 16, 1)
        
        # Vezérlés info
        if current_mode == "manual":
            oled.text("A: speed B: back", 0, 24, 1)
        else:
            oled.text("B: back", 0, 24, 1)
        
        # Animált ventilátor ikon
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_animation_update) > ANIMATION_SPEED:
            animation_frame = (animation_frame + 1) % len(fan_frames)
            last_animation_update = current_time
        
        draw_fan_icon(112, 8, animation_frame)
        
        oled.show()
    except Exception as e:
        print("Státusz képernyő hiba:", e)

def handle_menu_navigation():
    """Menü navigáció kezelése"""
    global current_menu, last_menu_press, last_select_press, in_menu, current_mode
    
    # Menu gomb - léptetés menüpontok között
    menu_pressed, last_menu_press = debounce_button(btn_menu, last_menu_press)
    if menu_pressed:
        current_menu = (current_menu + 1) % len(menu_items)
        print("Menü lépés:", menu_items[current_menu])
    
    # Select gomb - belépés kiválasztott módba
    select_pressed, last_select_press = debounce_button(btn_select, last_select_press)
    if select_pressed:
        print("Kiválasztva:", menu_items[current_menu])
        if current_menu == 0:  # AUTO
            current_mode = "auto"
            in_menu = False
            print("Automatikus mód aktiválva")
        elif current_menu == 1:  # MANUAL
            current_mode = "manual"
            in_menu = False
            print("Manuális mód aktiválva")

def handle_auto_mode():
    """Automatikus mód kezelése"""
    global current_speed_index, current_speed_percent, last_auto_step
    global in_menu, last_menu_press
    
    current_time = utime.ticks_ms()
    
    # Automatikus léptetés
    if utime.ticks_diff(current_time, last_auto_step) > AUTO_STEP_TIME:
        current_speed_index = (current_speed_index + 1) % len(PWM_STEPS)
        current_speed_percent = PWM_STEPS[current_speed_index]
        set_fan_speed(current_speed_percent)
        last_auto_step = current_time
        print("Auto mód, PWM:", current_speed_percent)
    
    # Menu gomb - vissza a főmenübe
    menu_pressed, last_menu_press = debounce_button(btn_menu, last_menu_press)
    if menu_pressed:
        print("Vissza a főmenübe")
        in_menu = True
        current_mode = None
        set_fan_speed(0)

def handle_manual_mode():
    """Manuális mód kezelése"""
    global current_speed_index, current_speed_percent, last_select_press, last_menu_press
    global in_menu
    
    # Select gomb - sebességváltás
    select_pressed, last_select_press = debounce_button(btn_select, last_select_press)
    if select_pressed:
        current_speed_index = (current_speed_index + 1) % len(PWM_STEPS)
        current_speed_percent = PWM_STEPS[current_speed_index]
        set_fan_speed(current_speed_percent)
        print("Manuális lépés, PWM:", current_speed_percent)
    
    # Menu gomb - vissza a főmenübe
    menu_pressed, last_menu_press = debounce_button(btn_menu, last_menu_press)
    if menu_pressed:
        print("Vissza a főmenübe")
        in_menu = True
        current_mode = None
        set_fan_speed(0)

def update_rpm():
    """RPM frissítése"""
    global last_rpm_measure
    
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_rpm_measure) >= RPM_MEASURE_INTERVAL:
        calculate_rpm()
        last_rpm_measure = current_time

# ========== FŐPROGRAM ==========
def main():
    """Főprogram"""
    global in_menu, current_mode, current_speed_percent
    
    print("Pandafix - Fan Tester indítása...")
    
    # Splash screen
    show_splash_screen()
    
    # Kezdeti sebesség beállítása
    current_speed_percent = PWM_STEPS[current_speed_index]
    set_fan_speed(0)
    
    print("Főciklus indítása...")
    
    # Főciklus
    while True:
        try:
            if in_menu:
                # Menü mód
                show_menu()
                handle_menu_navigation()
                
            else:
                # Működési mód (auto/manual)
                if current_mode == "auto":
                    handle_auto_mode()
                elif current_mode == "manual":
                    handle_manual_mode()
                
                # Státusz képernyő
                show_status_screen()
            
            # RPM frissítése
            update_rpm()
            
            # Kis várakozás
            utime.sleep_ms(50)
            
            # Garbage collection
            if utime.ticks_ms() % 10000 < 100:
                gc.collect()
                
        except KeyboardInterrupt:
            print("Program megszakítva")
            set_fan_speed(0)
            break
        except Exception as e:
            print("Futási hiba:", e)
            set_fan_speed(0)
            utime.sleep_ms(1000)

# Program indítása
if __name__ == "__main__":
    main()