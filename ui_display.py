# Fájl helye: /ui_display.py
# Funkció: OLED kijelző kezelése, menük kirajzolása, animációk és rendszer hőmérséklet mérése.
# Tartalmazza a gördülő szöveg (késleltetéssel és maszkolással) és a Star Wars effektus logikáját.

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

# Görgetés beállítások
SCROLL_START_DELAY_MS = 500   # Mennyi ideig álljon a szöveg, mielőtt elindul
ARROW_MARGIN = 12             # Hely a nyilaknak pixelben (bal és jobb oldalon)

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

    def _draw_scrolling_text_horizontal(self, text, y_pos, start_time, margin=0):
        """
        Vízszintesen gördülő szöveg (Marquee).
        - start_delay: vár, mielőtt elindul.
        - margin: kihagyja a helyet a széleken (pl. nyilaknak), de a szöveg mögötte fut.
          A hívónak kell maszkolnia a széleket, ha le akarja vágni a szöveget.
        """
        text_width = len(text) * 8
        # A rendelkezésre álló szélesség a margók között
        window_width = config.OLED_WIDTH - (2 * margin)
        
        # Számított X pozíció a margóhoz igazítva
        base_x = margin 

        if text_width <= window_width:
            # Ha kifér, középre igazítjuk a rendelkezésre álló ablakban
            x_pos = margin + (window_width - text_width) // 2
            self.oled.text(text, x_pos, y_pos, 1)
        else:
            # Ha nem fér ki, görgetés logika
            elapsed = time.ticks_diff(time.ticks_ms(), start_time)
            
            # Késleltetés ellenőrzése
            if elapsed < SCROLL_START_DELAY_MS:
                # Még várakozunk: A szöveg eleje látszik (balra igazítva a margónál)
                self.oled.text(text, base_x, y_pos, 1)
            else:
                # Görgetés fázis
                # Levonjuk a késleltetési időt a számításból
                scroll_elapsed = elapsed - SCROLL_START_DELAY_MS
                
                # Teljes út hossza: bejön jobbról (vagy a végétől), kimegy balra
                # A kérés szerint: "folyjon a szöveg jobbról balra" - ez a standard marquee, 
                # de a delay miatt inkább onnan indulunk, ahol állt, és kimegy balra.
                
                # 1. opció: A szöveg eleje látszik, majd elindul balra, amíg a vége be nem ér, majd szünet, majd reset.
                # Ez olvashatóbb, mint a folyamatosan áthúzó szöveg.
                
                # Út hossza: A szöveg teljes hossza plusz a képernyő szélessége a resethez
                # De a felhasználó azt kérte: "eleje látszik... majd elkezd futni"
                
                # Mennyit kell menni, hogy a szöveg vége is látsszon és eltűnjön?
                travel_distance = text_width + window_width 
                
                cycle_time_ms = int((travel_distance * 1000) / config.SCROLL_SPEED_HORIZONTAL)
                total_cycle_time = cycle_time_ms + config.SCROLL_WAIT_MS
                
                current_cycle_time = scroll_elapsed % total_cycle_time
                
                if current_cycle_time < cycle_time_ms:
                    pixel_offset = int((current_cycle_time / cycle_time_ms) * travel_distance)
                    # Indulás: base_x (ahol állt)
                    # De ha travel_distance-t használunk, az folyamatos futás.
                    # Módosított logika a kéréshez igazodva (onnan indul ahol állt):
                    
                    # Induló pozíció: base_x. Cél: teljesen kimegy balra (-text_width).
                    # Utána visszajön jobbról vagy resetel.
                    # Egyszerűsítsük a standard marquee-re, de a delay után.
                    
                    # Ha a delay letelt, folyamatosan csúszik balra az x pozíció
                    # Kezdőpont: base_x
                    x_pos = base_x - pixel_offset
                    
                    # Ha már nagyon kiment balra, és jönne be jobbról (ciklus)
                    if x_pos < -text_width:
                        x_pos += (text_width + window_width + 20) # +20 pixel rés
                        
                    self.oled.text(text, x_pos, y_pos, 1)
                else:
                    # Várakozás a ciklus végén (üres képernyő vagy újraindulás előtt)
                    pass

    def _draw_arrows_and_mask(self, y_pos):
        """Kirajzolja a maszkoló téglalapokat és a nyilakat."""
        # Bal oldal törlése (maszkolás)
        self.oled.fill_rect(0, y_pos, ARROW_MARGIN, 8, 0)
        # Jobb oldal törlése (maszkolás)
        self.oled.fill_rect(config.OLED_WIDTH - ARROW_MARGIN, y_pos, ARROW_MARGIN, 8, 0)
        
        # Nyilak kirajzolása
        self.oled.text("<", 0, y_pos, 1)
        self.oled.text(">", config.OLED_WIDTH - 8, y_pos, 1)

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
        """Főmenü kirajzolása maszkolással és nyilakkal."""
        self.clear()
        self.oled.text(self.get_text(title_key), 10, 0, 1)
        
        key = items_keys[selected_idx]
        item_text = self.get_text(key)
        
        # 1. Szöveg kirajzolása (görgetve, margóval számolva)
        self._draw_scrolling_text_horizontal(item_text, 16, start_time, margin=ARROW_MARGIN)
        
        # 2. Szélek letakarása és nyilak rárajzolása
        self._draw_arrows_and_mask(16)
        
        self.show()

    def draw_language_selector(self, lang_list, selected_idx, start_time):
        """Nyelvválasztó képernyő maszkolással."""
        self.clear()
        self.oled.text(self.get_text("mode_language"), 0, 0, 1)
        
        try:
            lang_code = lang_list[selected_idx]
            lang_data = locales.get_locale(lang_code)
            lang_name = lang_data.get("lang_name", lang_code)
            
            # Szöveg
            self._draw_scrolling_text_horizontal(lang_name, 16, start_time, margin=ARROW_MARGIN)
            
            # Maszk és nyilak
            self._draw_arrows_and_mask(16)
            
        except Exception as e:
            print(f"UI Error: {e}")
            self.oled.text("Error", 30, 16, 1)
        
        self.show()

    def draw_value_selector(self, title_key, current_val, unit_key=""):
        """Értékválasztó képernyő maszkolással."""
        self.clear()
        self.oled.text(self.get_text(title_key), 0, 0, 1)
        
        # Érték szövegének formázása
        if unit_key and unit_key != "%":
            val_text = f"{current_val} {self.get_text(unit_key)}"
        elif unit_key == "%":
             val_text = f"{current_val}%"
        else:
            val_text = str(current_val)
            
        # Mivel a számok rövidek, itt nem feltétlenül kell görgetés, 
        # de a konzisztencia és a nyilak miatt használjuk a biztonságos kirajzolást.
        text_pos_x = max(0, (config.OLED_WIDTH - (len(val_text) * 8)) // 2)
        
        # Itt egyszerűsítünk: a számok kiférnek, nem kell görgetni, de a nyilakat rajzoljuk.
        self.oled.text(val_text, text_pos_x, 16, 1)
        
        # Nyilak (itt nem kell maszkolni, mert a szám rövid)
        self.oled.text("<", 0, 16, 1)
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

# Utolsó módosítás: 2026. február 06. 10:00:00