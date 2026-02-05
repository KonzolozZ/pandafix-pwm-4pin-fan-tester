# Fájl helye: /main.py
# Funkció: A rendszer inicializálása és a fő eseményhurok (state machine) futtatása aszinkron módon. Többnyelvű és perzisztens beállításokkal.

import uasyncio as asyncio
import config
from fan_control import FanController
from ui_display import DisplayManager
from inputs import Button
from settings_manager import SettingsManager
import gc
import time

class App:
    def __init__(self):
        print("Rendszer inditasa...")
        
        # Beállítások betöltése
        self.settings = SettingsManager()
        
        # UI és Ventilátor init
        self.display = DisplayManager(self.settings)
        self.fan = FanController()
        
        # Menü struktúra (nyelvi kulcsok)
        self.MENU_KEYS = ["mode_auto", "mode_manual", "mode_target", "mode_language"]
        self.MENU_IDS = ["AUTO", "MANUAL", "TARGET", "LANG"]
        
        # Nyelvek listája
        self.LANG_CODES = config.SUPPORTED_LANGUAGES
        
        # Állapotváltozók
        self.state = "SPLASH"
        self.menu_idx = 0
        self.lang_menu_idx = 0
        
        # Teszt változók
        self.manual_pwm_idx = 0
        self.pwm_steps = [0, 20, 40, 60, 80, 100]
        self.auto_step_idx = 0
        self.last_auto_step_time = 0
        
        # Target RPM változók
        self.target_rpm_list = [500, 800, 1000, 1200, 1500, 2000, 2500, 3000]
        self.target_rpm_idx = 2
        
        # Gomb esemény flag-ek
        self.flag_menu_pressed = False
        self.flag_select_pressed = False

        # Gomb objektumok
        self.btn_menu = Button(config.PIN_MENU, self._cb_menu_press)
        self.btn_select = Button(config.PIN_SELECT, self._cb_select_press)

    def _cb_menu_press(self):
        self.flag_menu_pressed = True

    def _cb_select_press(self):
        self.flag_select_pressed = True

    async def run(self):
        """Fő aszinkron hurok."""
        # Splash screen
        self.display.draw_splash()
        await asyncio.sleep_ms(config.SPLASH_TIME_MS)
        self.state = "MENU"
        
        # Indítjuk a folyamatos feladatokat
        asyncio.create_task(self._task_update_fan())
        asyncio.create_task(self._task_display())
        
        # Fő logikai hurok
        while True:
            await self._handle_logic()
            await asyncio.sleep_ms(50)

    async def _task_update_fan(self):
        """Háttérfolyamat: RPM mérés és vezérlés."""
        while True:
            self.fan.calculate_rpm()
            await asyncio.sleep_ms(100)

    async def _task_display(self):
        """Háttérfolyamat: Képernyő frissítése."""
        while True:
            if self.state == "MENU":
                self.display.draw_menu(self.MENU_KEYS, self.menu_idx)
            
            elif self.state == "SELECT_LANG":
                self.display.draw_language_selector(self.LANG_CODES, self.lang_menu_idx)
                
            elif self.state == "MESSAGE_SAVED":
                self.display.draw_message("saved")
                
            elif self.state == "RUN_AUTO":
                self.display.draw_test_screen(
                    "mode_auto", 
                    self.fan.current_duty_percent, 
                    self.fan.current_rpm,
                    self.fan.stall_detected
                )
                
            elif self.state == "RUN_MANUAL":
                self.display.draw_test_screen(
                    "mode_manual", 
                    self.fan.current_duty_percent, 
                    self.fan.current_rpm,
                    self.fan.stall_detected
                )
                
            elif self.state == "RUN_TARGET":
                 self.display.draw_test_screen(
                    "mode_target", 
                    self.fan.current_duty_percent, 
                    self.fan.current_rpm,
                    self.fan.stall_detected,
                    target_rpm=self.target_rpm_list[self.target_rpm_idx]
                )
            
            await asyncio.sleep_ms(100)

    async def _handle_logic(self):
        """Állapotgép logika."""
        current_time = time.ticks_ms()
        
        # --- MENÜ ÁLLAPOT ---
        if self.state == "MENU":
            self.fan.set_duty_percent(0)
            self.fan.disable_target_mode()
            
            if self.flag_menu_pressed:
                self.menu_idx = (self.menu_idx + 1) % len(self.MENU_KEYS)
                self.flag_menu_pressed = False
                
            if self.flag_select_pressed:
                mode = self.MENU_IDS[self.menu_idx]
                if mode == "AUTO":
                    self.state = "RUN_AUTO"
                    self.auto_step_idx = 0
                    self.last_auto_step_time = current_time
                elif mode == "MANUAL":
                    self.state = "RUN_MANUAL"
                    self.manual_pwm_idx = 1
                    self.fan.set_duty_percent(self.pwm_steps[self.manual_pwm_idx])
                elif mode == "TARGET":
                    self.state = "RUN_TARGET"
                    self.fan.set_target_rpm(self.target_rpm_list[self.target_rpm_idx])
                elif mode == "LANG":
                    self.state = "SELECT_LANG"
                    # Megkeressük az aktuális nyelvet a listában
                    curr = self.settings.get("language")
                    try:
                        self.lang_menu_idx = self.LANG_CODES.index(curr)
                    except ValueError:
                        self.lang_menu_idx = 0
                
                self.flag_select_pressed = False

        # --- NYELVVÁLASZTÁS ---
        elif self.state == "SELECT_LANG":
            if self.flag_menu_pressed:
                self.lang_menu_idx = (self.lang_menu_idx + 1) % len(self.LANG_CODES)
                self.flag_menu_pressed = False
            
            if self.flag_select_pressed:
                # Nyelv mentése
                new_lang = self.LANG_CODES[self.lang_menu_idx]
                self.settings.set("language", new_lang)
                self.display.update_language()
                
                # Visszajelzés
                self.state = "MESSAGE_SAVED"
                self.saved_message_start = current_time
                self.flag_select_pressed = False

        # --- ÜZENET MEGJELENÍTÉSE ---
        elif self.state == "MESSAGE_SAVED":
            if time.ticks_diff(current_time, self.saved_message_start) > 1500:
                self.state = "MENU"
            # Gombok törlése
            self.flag_menu_pressed = False
            self.flag_select_pressed = False

        # --- AUTO TESZT ---
        elif self.state == "RUN_AUTO":
            if self.flag_menu_pressed:
                self.state = "MENU"
                self.flag_menu_pressed = False
                
            if time.ticks_diff(current_time, self.last_auto_step_time) > config.AUTO_STEP_INTERVAL_MS:
                self.auto_step_idx = (self.auto_step_idx + 1) % len(self.pwm_steps)
                duty = self.pwm_steps[self.auto_step_idx]
                self.fan.set_duty_percent(duty)
                self.last_auto_step_time = current_time
            
            if self.flag_select_pressed:
                self.flag_select_pressed = False

        # --- MANUÁLIS TESZT ---
        elif self.state == "RUN_MANUAL":
            if self.flag_menu_pressed:
                self.state = "MENU"
                self.flag_menu_pressed = False
                
            if self.flag_select_pressed:
                self.manual_pwm_idx = (self.manual_pwm_idx + 1) % len(self.pwm_steps)
                duty = self.pwm_steps[self.manual_pwm_idx]
                self.fan.set_duty_percent(duty)
                self.flag_select_pressed = False

        # --- TARGET RPM ---
        elif self.state == "RUN_TARGET":
            if self.flag_menu_pressed:
                self.state = "MENU"
                self.fan.disable_target_mode()
                self.flag_menu_pressed = False
            
            if self.flag_select_pressed:
                self.target_rpm_idx = (self.target_rpm_idx + 1) % len(self.target_rpm_list)
                new_target = self.target_rpm_list[self.target_rpm_idx]
                self.fan.set_target_rpm(new_target)
                self.flag_select_pressed = False
        
        # Memória tisztítás
        if current_time % 10000 < 50:
            gc.collect()

if __name__ == "__main__":
    app = App()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("Leallitas...")
        # Reset ventilátor
        from machine import PWM, Pin
        pwm = PWM(Pin(config.PIN_PWM))
        pwm.duty_u16(0)
    except Exception as e:
        print("Hiba:", e)
        import sys
        sys.print_exception(e)
        # Hiba esetén biztonsági leállás
        from machine import PWM, Pin
        pwm = PWM(Pin(config.PIN_PWM))
        pwm.duty_u16(0)

# Utolsó módosítás: 2026. február 05. 22:20:00