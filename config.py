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

# ========== NYELVI BEÁLLÍTÁSOK ==========
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "hu", "de", "es", "fr", "it"]

# ========== DEBUG ==========
DEBUG_MODE = True

# Utolsó módosítás: 2026. február 05. 22:20:00