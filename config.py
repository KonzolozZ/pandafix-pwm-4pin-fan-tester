# Fájl helye: /config.py
# Funkció: A rendszer globális beállításainak és pin kiosztásának tárolása.

from micropython import const

# ========== PIN KIOSZTÁS ==========
PIN_PWM = 16       # Ventilátor PWM kimenet
PIN_TACH = 17      # Ventilátor TACH bemenet
PIN_MENU = 14      # "B" gomb (Menü/Vissza)
PIN_SELECT = 15    # "A" gomb (Kiválaszt/Léptet)
PIN_I2C_SCL = 5    # OLED SCL
PIN_I2C_SDA = 4    # OLED SDA

# ========== KIJELZŐ BEÁLLÍTÁSOK ==========
OLED_WIDTH = 128
OLED_HEIGHT = 32
I2C_FREQ = 400000

# ========== VENTILÁTOR BEÁLLÍTÁSOK ==========
PWM_FREQ = 25000       # 25kHz Intel szabvány szerint
PWM_MIN_DUTY = 0
PWM_MAX_DUTY = 65535
TACH_PULSES_PER_REV = 2 # Impulzus per fordulat (szabványos ventilátor)

# ========== LOGIKA BEÁLLÍTÁSOK ==========
SPLASH_TIME_MS = 2000
AUTO_STEP_INTERVAL_MS = 5000  # Auto módban lépésköz
RPM_UPDATE_INTERVAL_MS = 1000 # RPM mérés gyakorisága
TARGET_RPM_TOLERANCE = 100    # Cél RPM tűréshatár (+/-)
STALL_THRESHOLD_DUTY = 30     # % PWM, ami felett elakadásnak számít a 0 RPM
MOVING_AVERAGE_SAMPLES = 5    # Hány mérést átlagoljon

# ========== ALAPÉRTELMEZETT BEÁLLÍTÁSOK ==========
DEFAULT_LANGUAGE = "en"
DEFAULT_PWM_STEP = 20         # %-os ugrás manuális módban
DEFAULT_DEBOUNCE_MS = 200     # Gomb érzéketlenségi idő (pergésmentesítés)

# Opciók a beállítások menühöz
PWM_STEP_OPTIONS = [5, 10, 20, 25]
DEBOUNCE_OPTIONS = [50, 100, 200, 300, 500] # ms
SUPPORTED_LANGUAGES = ["en", "hu", "de", "es", "fr", "it"]

# Animációs sebességek
SCROLL_SPEED_HORIZONTAL = 40  # Pixel/mp (vízszintes görgetés)
SCROLL_SPEED_VERTICAL = 15    # Pixel/mp (About screen függőleges)
SCROLL_WAIT_MS = 1000         # Várakozás görgetés után (ms)

# ========== DEBUG ==========
DEBUG_MODE = True

# Utolsó módosítás: 2026. február 06. 09:40:00