# Fájl helye: /main.py
# Funkció: A rendszer inicializálása és a fő eseményhurok. Beállítások, About, Gördülő szövegek támogatása.

import uasyncio as asyncio
import config
from fan_control import FanController
from ui_display import DisplayManager
from inputs import Button
from settings_manager import SettingsManager
import gc
import time
import locales

class App:
    def __init__(self):
        print("Rendszer inditasa...")
        
        # Beállítások betöltése
        self.settings = SettingsManager()
        
        # UI és Ventilátor init
        self.display = DisplayManager(self.settings)
        self.fan = FanController()
        
        # Főmenü struktúra
        self.MAIN_MENU_KEYS = ["mode_auto", "mode_manual", "mode_target", "mode_settings", "mode_about"]
        self.MAIN_MENU_IDS = ["AUTO", "MANUAL", "TARGET", "SETTINGS", "ABOUT"]
        
        # Beállítások menü struktúra
        self.SETT_MENU_KEYS = ["set_lang", "set_step", "set_debounce", "back"]
        self.SETT_MENU_IDS = ["LANG", "STEP", "DEBOUNCE", "BACK"]
        
        # Listák
        self.LANG_CODES = config.SUPPORTED_LANGUAGES
        self.STEP_OPTIONS = config.PWM_STEP_OPTIONS
        self.DEBOUNCE_OPTIONS = config.DEBOUNCE_OPTIONS
        
        # Állapotváltozók
        self.state = "SPLASH"
        self.menu_idx = 0
        self.settings_menu_idx = 0
        
        # Időzítők görgetéshez
        self.state_start_time = time.ticks_ms()
        self.last_menu_change_time = time.ticks_ms()
        
        # Selector indexek
        self.lang_sel_idx = 0
        self.step_sel_idx = 0
        self.debounce_sel_idx = 0
        
        # Teszt változók
        self.manual_pwm_idx = 0
        self.pwm_steps = [] 
        self.auto_step_idx = 0
        self.last_auto_step_time = 0
        self.target_rpm_list = [500, 800, 1000, 1200, 1500, 2000, 2500, 3000]
        self.target_rpm_idx = 2
        
        # Gomb esemény flag-ek
        self.flag_menu_pressed = False
        self.flag_select_pressed = False

        # Gomb objektumok
        initial_debounce = self.settings.get("debounce_ms")
        self.btn_menu = Button(config.PIN_MENU, self._cb_menu_press, initial_debounce)
        self.btn_select = Button(config.PIN_SELECT, self._cb_select_press, initial_debounce)

    def _cb_menu_press(self):
        self.flag_menu_pressed = True

    def _cb_select_press(self):
        self.flag_select_pressed = True
        
    def _init_selector_indices(self):
        """Beállítja a kiválasztó indexeket."""
        curr_lang = self.settings.get("language")
        try:
            self.lang_sel_idx = self.LANG_CODES.index(curr_lang)
        except ValueError:
            self.lang_sel_idx = 0
            
        curr_step = self.settings.get("pwm_step")
        try:
            self.step_sel_idx = self.STEP_OPTIONS.index(curr_step)
        except ValueError:
            self.step_sel_idx = 0
            
        curr_deb = self.settings.get("debounce_ms")
        try:
            self.debounce_sel_idx = self.DEBOUNCE_OPTIONS.index(curr_deb)
        except ValueError:
            self.debounce_sel_idx = 2

    def _change_state(self, new_state):
        """Állapotváltás segédfüggvény az időzítők resetelésével."""
        self.state = new_state
        self.state_start_time = time.ticks_ms()
        # Ha menübe lépünk, reseteljük a görgetést is
        self.last_menu_change_time = self.state_start_time

    async def run(self):
        """Fő aszinkron hurok."""
        self.display.draw_splash()
        await asyncio.sleep_ms(config.SPLASH_TIME_MS)
        self._change_state("MENU")
        self._init_selector_indices()
        
        # Indítjuk a folyamatos feladatokat
        asyncio.create_task(self._task_update_fan())
        asyncio.create_task(self._task_display())
        
        # Fő logikai hurok
        while True:
            await self._handle_logic()
            await asyncio.sleep_ms(50)

    async def _task_update_fan(self):
        """RPM mérés."""
        while True:
            self.fan.calculate_rpm()
            await asyncio.sleep_ms(100)

    async def _task_display(self):
        """Képernyő frissítése."""
        while True:
            try:
                # Menük esetén a last_menu_change_time-ot használjuk a görgetéshez,
                # hogy amikor a felhasználó vált, a szöveg elölről induljon.
                
                if self.state == "MENU":
                    self.display.draw_menu("menu_title", self.MAIN_MENU_KEYS, self.menu_idx, self.last_menu_change_time)
                
                elif self.state == "SETTINGS_MENU":
                     self.display.draw_menu("mode_settings", self.SETT_MENU_KEYS, self.settings_menu_idx, self.last_menu_change_time)
                
                elif self.state == "ABOUT":
                    self.display.draw_about_screen(self.state_start_time)

                elif self.state == "SELECT_LANG":
                    # Itt is görgethetjük a nyelv nevét ha hosszú
                    self.display.draw_language_selector(self.LANG_CODES, self.lang_sel_idx, self.last_menu_change_time)
                
                elif self.state == "SELECT_STEP":
                    val = self.STEP_OPTIONS[self.step_sel_idx]
                    self.display.draw_value_selector("set_step", val, "%")
                
                elif self.state == "SELECT_DEBOUNCE":
                    val = self.DEBOUNCE_OPTIONS[self.debounce_sel_idx]
                    self.display.draw_value_selector("set_debounce", val, "unit_ms")
                    
                elif self.state == "MESSAGE_SAVED":
                    self.display.draw_message("saved")
                    
                elif self.state == "RUN_AUTO":
                    self.display.draw_test_screen("mode_auto", self.fan.current_duty_percent, self.fan.current_rpm, self.fan.stall_detected)
                    
                elif self.state == "RUN_MANUAL":
                    self.display.draw_test_screen("mode_manual", self.fan.current_duty_percent, self.fan.current_rpm, self.fan.stall_detected)
                    
                elif self.state == "RUN_TARGET":
                     self.display.draw_test_screen("mode_target", self.fan.current_duty_percent, self.fan.current_rpm, self.fan.stall_detected, target_rpm=self.target_rpm_list[self.target_rpm_idx])
            
            except Exception as e:
                print(f"Display error: {e}")
            
            await asyncio.sleep_ms(50) # 20 FPS

    async def _handle_logic(self):
        """Állapotgép logika."""
        current_time = time.ticks_ms()
        
        # --- FŐMENÜ ---
        if self.state == "MENU":
            self.fan.set_duty_percent(0)
            self.fan.disable_target_mode()
            
            if self.flag_menu_pressed:
                self.menu_idx = (self.menu_idx + 1) % len(self.MAIN_MENU_KEYS)
                self.last_menu_change_time = current_time # Reset scroll
                self.flag_menu_pressed = False
                
            if self.flag_select_pressed:
                mode = self.MAIN_MENU_IDS[self.menu_idx]
                if mode == "AUTO":
                    self._change_state("RUN_AUTO")
                    self.pwm_steps = [0, 20, 40, 60, 80, 100]
                    self.auto_step_idx = 0
                    self.last_auto_step_time = current_time
                elif mode == "MANUAL":
                    self._change_state("RUN_MANUAL")
                    step = self.settings.get("pwm_step")
                    self.pwm_steps = list(range(0, 101, step))
                    if self.pwm_steps[-1] != 100: self.pwm_steps.append(100)
                    self.manual_pwm_idx = 1 if len(self.pwm_steps) > 1 else 0
                    self.fan.set_duty_percent(self.pwm_steps[self.manual_pwm_idx])
                elif mode == "TARGET":
                    self._change_state("RUN_TARGET")
                    self.fan.set_target_rpm(self.target_rpm_list[self.target_rpm_idx])
                elif mode == "SETTINGS":
                    self._change_state("SETTINGS_MENU")
                    self.settings_menu_idx = 0
                elif mode == "ABOUT":
                    self._change_state("ABOUT")
                
                self.flag_select_pressed = False

        # --- BEÁLLÍTÁSOK MENÜ ---
        elif self.state == "SETTINGS_MENU":
            if self.flag_menu_pressed:
                self.settings_menu_idx = (self.settings_menu_idx + 1) % len(self.SETT_MENU_KEYS)
                self.last_menu_change_time = current_time
                self.flag_menu_pressed = False
                
            if self.flag_select_pressed:
                item_id = self.SETT_MENU_IDS[self.settings_menu_idx]
                if item_id == "LANG":
                    self._change_state("SELECT_LANG")
                    self.last_menu_change_time = current_time
                elif item_id == "STEP":
                    self._change_state("SELECT_STEP")
                elif item_id == "DEBOUNCE":
                    self._change_state("SELECT_DEBOUNCE")
                elif item_id == "BACK":
                    self._change_state("MENU")
                self.flag_select_pressed = False

        # --- NYELVVÁLASZTÁS ---
        elif self.state == "SELECT_LANG":
            if self.flag_menu_pressed:
                self.lang_sel_idx = (self.lang_sel_idx + 1) % len(self.LANG_CODES)
                self.last_menu_change_time = current_time
                self.flag_menu_pressed = False
            
            if self.flag_select_pressed:
                new_lang = self.LANG_CODES[self.lang_sel_idx]
                self.settings.set("language", new_lang)
                self.display.update_language()
                self._save_and_exit_submenu(current_time)

        # --- PWM LÉPÉS VÁLASZTÁS ---
        elif self.state == "SELECT_STEP":
            if self.flag_menu_pressed:
                self.step_sel_idx = (self.step_sel_idx + 1) % len(self.STEP_OPTIONS)
                self.flag_menu_pressed = False
            if self.flag_select_pressed:
                new_step = self.STEP_OPTIONS[self.step_sel_idx]
                self.settings.set("pwm_step", new_step)
                self._save_and_exit_submenu(current_time)

        # --- DEBOUNCE VÁLASZTÁS ---
        elif self.state == "SELECT_DEBOUNCE":
            if self.flag_menu_pressed:
                self.debounce_sel_idx = (self.debounce_sel_idx + 1) % len(self.DEBOUNCE_OPTIONS)
                self.flag_menu_pressed = False
            if self.flag_select_pressed:
                new_deb = self.DEBOUNCE_OPTIONS[self.debounce_sel_idx]
                self.settings.set("debounce_ms", new_deb)
                self.btn_menu.update_debounce(new_deb)
                self.btn_select.update_debounce(new_deb)
                self._save_and_exit_submenu(current_time)
        
        # --- ABOUT ---
        elif self.state == "ABOUT":
            # Bármelyik gombra kilép
            if self.flag_menu_pressed or self.flag_select_pressed:
                self._change_state("MENU")
                self.flag_menu_pressed = False
                self.flag_select_pressed = False

        # --- EGYÉB TESZT MÓDOK ---
        # (Auto, Manual, Target logikája ugyanaz, mint előzőleg, csak a visszalépésnél a MENU-be megy)
        elif self.state == "MESSAGE_SAVED":
            if time.ticks_diff(current_time, self.saved_message_start) > 1500:
                self._change_state("SETTINGS_MENU")
            self.flag_menu_pressed = False
            self.flag_select_pressed = False

        elif self.state == "RUN_AUTO":
            if self.flag_menu_pressed:
                self._change_state("MENU")
                self.flag_menu_pressed = False
            if time.ticks_diff(current_time, self.last_auto_step_time) > config.AUTO_STEP_INTERVAL_MS:
                self.auto_step_idx = (self.auto_step_idx + 1) % len(self.pwm_steps)
                self.fan.set_duty_percent(self.pwm_steps[self.auto_step_idx])
                self.last_auto_step_time = current_time
            self.flag_select_pressed = False

        elif self.state == "RUN_MANUAL":
            if self.flag_menu_pressed:
                self._change_state("MENU")
                self.flag_menu_pressed = False
            if self.flag_select_pressed:
                self.manual_pwm_idx = (self.manual_pwm_idx + 1) % len(self.pwm_steps)
                self.fan.set_duty_percent(self.pwm_steps[self.manual_pwm_idx])
                self.flag_select_pressed = False

        elif self.state == "RUN_TARGET":
            if self.flag_menu_pressed:
                self._change_state("MENU")
                self.fan.disable_target_mode()
                self.flag_menu_pressed = False
            if self.flag_select_pressed:
                self.target_rpm_idx = (self.target_rpm_idx + 1) % len(self.target_rpm_list)
                self.fan.set_target_rpm(self.target_rpm_list[self.target_rpm_idx])
                self.flag_select_pressed = False

        if current_time % 10000 < 50:
            gc.collect()

    def _save_and_exit_submenu(self, current_time):
        """Beállítás mentése utáni logika."""
        self.state = "MESSAGE_SAVED"
        self.saved_message_start = current_time
        self.flag_select_pressed = False

if __name__ == "__main__":
    app = App()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("Leallitas...")
        from machine import PWM, Pin
        pwm = PWM(Pin(config.PIN_PWM))
        pwm.duty_u16(0)
    except Exception as e:
        print("Hiba:", e)
        import sys
        sys.print_exception(e)
        from machine import PWM, Pin
        pwm = PWM(Pin(config.PIN_PWM))
        pwm.duty_u16(0)

# Utolsó módosítás: 2026. február 06. 09:20:00