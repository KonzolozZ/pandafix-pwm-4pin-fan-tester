# Fájl helye: /ui_display.py
# Funkció: OLED kijelző kezelése, menük kirajzolása, animációk és rendszer hőmérséklet mérése.
# Tartalmazza a gördülő szöveg és a Star Wars effektus logikáját.

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

    def _draw_scrolling_text_horizontal(self, text, y_pos, start_time):
        """Vízszintesen gördülő szöveg (Marquee) - Jobbról balra, szünettel."""
        text_width = len(text) * 8
        screen_width = config.OLED_WIDTH
        
        if text_width <= screen_width:
            # Ha kifér, középre igazítjuk
            x_pos = (screen_width - text_width) // 2
            self.oled.text(text, x_pos, y_pos, 1)
        else:
            # Ha nem fér ki, görgetés
            elapsed = time.ticks_diff(time.ticks_ms(), start_time)
            
            # Teljes út hossza: bejön jobbról, kimegy balra
            total_travel_pixels = screen_width + text_width
            
            # Idő egy ciklushoz
            cycle_time_ms = int((total_travel_pixels * 1000) / config.SCROLL_SPEED_HORIZONTAL)
            total_cycle_time = cycle_time_ms + config.SCROLL_WAIT_MS
            
            current_cycle_time = elapsed % total_cycle_time
            
            if current_cycle_time < cycle_time_ms:
                # Mozgás fázis
                pixel_offset = int((current_cycle_time / cycle_time_ms) * total_travel_pixels)
                x_pos = screen_width - pixel_offset
                self.oled.text(text, x_pos, y_pos, 1)
            else:
                # Várakozás fázis (üres képernyő)
                pass 

    def draw_about_screen(self, start_time):
        """Star Wars stílusú, lentről felfelé úszó szöveg."""
        self.clear()
        
        lines = self.get_text("about_text")
        line_height = 10
        total_text_height = len(lines) * line_height
        screen_h = config.OLED_HEIGHT
        
        elapsed = time.ticks_diff(time.ticks_ms(), start_time)
        # Pixel eltolás lentről felfelé
        pixel_shift = int((elapsed / 1000) * config.SCROLL_SPEED_VERTICAL)
        
        # Ciklus: amíg az utolsó sor is el nem hagyja a képernyőt
        cycle_pixels = total_text_height + screen_h
        current_shift = pixel_shift % cycle_pixels
        
        start_y_on_screen = screen_h - current_shift
        
        for i, line in enumerate(lines):
            y = start_y_on_screen + (i * line_height)
            # Csak azt rajzoljuk ki, ami a képernyőn van (optimalizálás)
            if -line_height < y < screen_h:
                text_width = len(line) * 8
                x = (config.OLED_WIDTH - text_width) // 2
                self.oled.text(line, x, int(y), 1)
                
        self.show()

    def draw_menu(self, title_key, items_keys, selected_idx, start_time):
        """Főmenü kirajzolása."""
        self.clear()
        self.oled.text(self.get_text(title_key), 10, 0, 1)
        
        # Navigációs nyilak
        self.oled.text("<", 0, 16, 1)
        self.oled.text(">", config.OLED_WIDTH - 8, 16, 1)
        
        # Szöveg görgetéssel
        key = items_keys[selected_idx]
        item_text = self.get_text(key)
        self._draw_scrolling_text_horizontal(item_text, 16, start_time)
        
        self.show()

    def draw_language_selector(self, lang_list, selected_idx, start_time):
        """Nyelvválasztó képernyő."""
        self.clear()
        self.oled.text(self.get_text("mode_language"), 0, 0, 1)
        
        try:
            lang_code = lang_list[selected_idx]
            # A nyelv saját neve
            lang_data = locales.get_locale(lang_code)
            lang_name = lang_data.get("lang_name", lang_code)
            
            self.oled.text("<", 0, 16, 1)
            self.oled.text(">", config.OLED_WIDTH - 8, 16, 1)
            # Itt is görgetjük, ha a nyelv neve hosszú lenne
            self._draw_scrolling_text_horizontal(lang_name, 16, start_time)
        except Exception as e:
            # Fallback hiba esetén, hogy ne fagyjon le
            print(f"UI Error: {e}")
            self.oled.text("Error", 30, 16, 1)
        
        self.show()

    def draw_value_selector(self, title_key, current_val, unit_key=""):
        """Értékválasztó képernyő (pl. pwm lépés, debounce)."""
        self.clear()
        self.oled.text(self.get_text(title_key), 0, 0, 1)
        
        # Érték szövegének formázása
        if unit_key and unit_key != "%":
            val_text = f"{current_val} {self.get_text(unit_key)}"
        elif unit_key == "%":
             val_text = f"{current_val}%"
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
        """Teszt képernyő kirajzolása."""
        self.clear()
        
        # 1. sor: Mód és Hőmérséklet
        mode_str = self.get_text(mode_key)
        if len(mode_str) > 11: 
            mode_str = mode_str[:11]
            
        self.oled.text(mode_str, 0, 0, 1)
        self._draw_statusbar(self.sys_mon.get_temperature())
        
        # 2. sor: Adatok
        if is_stall:
             self.oled.text(self.get_text("stall_alert"), 0, 12, 1)
        else:
            if target_rpm is not None:
                self.oled.text(f"{self.get_text('target')}:{target_rpm}", 0, 12, 1)
            else:
                self.oled.text(f"{self.get_text('pwm')}:{pwm_percent}%", 0, 12, 1)
            
            # 3. sor: RPM
            self.oled.text(f"{self.get_text('rpm')}:{rpm}", 0, 22, 1)
            
        # Ikon (jobb oldalon lent)
        should_animate = not is_stall and pwm_percent > 0
        self._draw_fan_icon(110, 16, should_animate)
        
        self.show()

# Utolsó módosítás: 2026. február 06. 09:40:00