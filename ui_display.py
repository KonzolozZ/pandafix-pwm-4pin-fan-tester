# Fájl helye: /ui_display.py
# Funkció: OLED kijelző kezelése, menük kirajzolása, animációk és rendszer hőmérséklet mérése. Többnyelvű támogatással.

from machine import I2C, Pin, ADC
from ssd1306 import SSD1306_I2C
import config
import locales
import time

# Animációs képkockák
FAN_ICON = [
    [0x18, 0x3C, 0x7E, 0xFF, 0xFF, 0x7E, 0x3C, 0x18],
    [0x24, 0x42, 0xBD, 0xFF, 0xFF, 0xBD, 0x42, 0x24],
    [0x18, 0x3C, 0x7E, 0xFF, 0xFF, 0x7E, 0x3C, 0x18],
    [0x42, 0x24, 0xBD, 0xFF, 0xFF, 0xBD, 0x24, 0x42]
]

class SystemMonitor:
    def __init__(self):
        self.sensor = ADC(4)
        
    def get_temperature(self):
        """RP2040 belső hőmérsékletének olvasása."""
        adc_value = self.sensor.read_u16()
        volt = (3.3 / 65535) * adc_value
        temperature = 27 - (volt - 0.706) / 0.001721
        return int(temperature)

class DisplayManager:
    def __init__(self, settings_mgr):
        self.i2c = I2C(0, scl=Pin(config.PIN_I2C_SCL), sda=Pin(config.PIN_I2C_SDA), freq=config.I2C_FREQ)
        self.oled = SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self.i2c)
        self.sys_mon = SystemMonitor()
        self.settings = settings_mgr
        
        # Aktuális nyelvi szótár betöltése
        self.current_lang = self.settings.get("language")
        self.strings = locales.get_locale(self.current_lang)
        
        self.anim_frame = 0
        self.last_anim_time = 0
        
    def update_language(self):
        """Frissíti a használt nyelvet a beállításokból."""
        lang = self.settings.get("language")
        if lang != self.current_lang:
            self.current_lang = lang
            self.strings = locales.get_locale(self.current_lang)

    def get_text(self, key):
        """Szöveg lekérése az aktuális nyelven."""
        return self.strings.get(key, key)
        
    def clear(self):
        self.oled.fill(0)
        
    def show(self):
        self.oled.show()

    def draw_splash(self):
        self.clear()
        self.oled.text(self.get_text("app_name"), 30, 5, 1)
        self.oled.text(self.get_text("app_sub"), 25, 20, 1)
        self.show()

    def _draw_fan_icon(self, x, y, animate=True):
        """Animált ikon kirajzolása."""
        if animate:
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_anim_time) > 200: 
                self.anim_frame = (self.anim_frame + 1) % len(FAN_ICON)
                self.last_anim_time = now
        
        bitmap = FAN_ICON[self.anim_frame]
        for r in range(8):
            for c in range(8):
                if (bitmap[r] >> (7-c)) & 1:
                    if x + c < config.OLED_WIDTH and y + r < config.OLED_HEIGHT:
                        self.oled.pixel(x + c, y + r, 1)

    def _draw_statusbar(self, temp_val):
        """Felső sáv hőmérséklettel."""
        # Jobb felső sarok: Hőmérséklet
        temp_str = f"{temp_val}C"
        self.oled.text(temp_str, config.OLED_WIDTH - (len(temp_str)*8), 0, 1)

    def draw_menu(self, title_key, items_keys, selected_idx):
        """Dinamikus menü kirajzolása. items_keys: a nyelvi kulcsok listája."""
        self.clear()
        self.oled.text(self.get_text(title_key), 10, 0, 1)
        
        # Navigációs nyilak és szöveg
        key = items_keys[selected_idx]
        item_text = self.get_text(key)
        
        # Középre igazítás
        text_pos_x = max(0, (config.OLED_WIDTH - (len(item_text) * 8)) // 2)
        
        self.oled.text("<", 0, 16, 1)
        self.oled.text(item_text, text_pos_x, 16, 1)
        self.oled.text(">", config.OLED_WIDTH - 8, 16, 1)
        
        self.show()

    def draw_value_selector(self, title_key, current_val, unit_key=""):
        """Értékválasztó képernyő (pl. nyelv, szám)."""
        self.clear()
        self.oled.text(self.get_text(title_key), 0, 0, 1)
        
        # Érték szövegének formázása
        if unit_key:
            val_text = f"{current_val} {self.get_text(unit_key)}"
        else:
            val_text = str(current_val)
            
        text_pos_x = max(0, (config.OLED_WIDTH - (len(val_text) * 8)) // 2)
        
        self.oled.text("<", 0, 16, 1)
        self.oled.text(val_text, text_pos_x, 16, 1)
        self.oled.text(">", config.OLED_WIDTH - 8, 16, 1)
        
        self.show()

    def draw_message(self, msg_key):
        """Egyszerű üzenet (pl. Mentve) megjelenítése."""
        self.clear()
        text = self.get_text(msg_key)
        x = (config.OLED_WIDTH - len(text) * 8) // 2
        self.oled.text(text, x, 12, 1)
        self.show()

    def draw_test_screen(self, mode_key, pwm_percent, rpm, is_stall, target_rpm=None):
        """Teszt képernyő kirajzolása (Auto, Manual, Target)."""
        self.clear()
        
        # 1. sor: Mód és Hőmérséklet
        mode_str = self.get_text(mode_key)
        # Ha túl hosszú a mód neve, vágjuk le
        if len(mode_str) > 11: 
            mode_str = mode_str[:11]
            
        self.oled.text(mode_str, 0, 0, 1)
        self._draw_statusbar(self.sys_mon.get_temperature())
        
        # 2. sor: Adatok
        if is_stall:
             self.oled.text(self.get_text("stall_alert"), 0, 12, 1)
        else:
            if target_rpm is not None:
                # Target módban a PWM helyett a Cél RPM látszik
                self.oled.text(f"{self.get_text('target')}:{target_rpm}", 0, 12, 1)
            else:
                # Normál módban PWM %
                self.oled.text(f"{self.get_text('pwm')}:{pwm_percent}%", 0, 12, 1)
            
            # 3. sor: RPM
            self.oled.text(f"{self.get_text('rpm')}:{rpm}", 0, 22, 1)
            
        # Ikon (jobb oldalon lent)
        # Ha a ventilátor áll (stall vagy 0 pwm), ne animáljon
        should_animate = not is_stall and pwm_percent > 0
        self._draw_fan_icon(110, 16, should_animate)
        
        self.show()

# Utolsó módosítás: 2026. február 06. 09:05:00