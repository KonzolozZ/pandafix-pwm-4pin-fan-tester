# Fájl helye: /fan_control.py
# Funkció: Ventilátor PWM vezérlése, fordulatszám mérése (mozgóátlaggal), elakadás figyelés.

from machine import Pin, PWM
import time
import config

class FanController:
    def __init__(self):
        # PWM inicializálás
        self.pwm = PWM(Pin(config.PIN_PWM))
        self.pwm.freq(config.PWM_FREQ)
        self.set_duty_percent(0)
        
        # TACH inicializálás
        self.tach_pin = Pin(config.PIN_TACH, Pin.IN, Pin.PULL_UP)
        self.tach_counter = 0
        self.tach_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._tach_isr)
        
        # RPM számítás változók
        self.current_rpm = 0
        self.last_measure_time = time.ticks_ms()
        self.rpm_history = [0] * config.MOVING_AVERAGE_SAMPLES # Ring buffer
        self.history_index = 0
        
        # Állapot
        self.current_duty_percent = 0
        self.stall_detected = False
        
        # Target RPM logika
        self.target_rpm = 0
        self.target_mode_active = False

    def _tach_isr(self, pin):
        """Megszakítás kezelő a fordulatszám jeladóhoz."""
        self.tach_counter += 1

    def set_duty_percent(self, percent):
        """PWM kitöltési tényező beállítása %-ban."""
        self.current_duty_percent = max(0, min(100, percent))
        duty_u16 = int((self.current_duty_percent / 100) * 65535)
        self.pwm.duty_u16(duty_u16)
        # Reset stall if speed changed significantly (optional logic)

    def calculate_rpm(self):
        """RPM számítása és mozgóátlag frissítése. (Periodikusan hívandó)"""
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self.last_measure_time)
        
        if dt >= config.RPM_UPDATE_INTERVAL_MS:
            # Atomic read and reset
            count = self.tach_counter
            self.tach_counter = 0
            self.last_measure_time = now
            
            # RPM képlet: (impulzusok / impulzus_per_fordulat) * (60000 / eltelt_idő_ms)
            raw_rpm = int((count / config.TACH_PULSES_PER_REV) * (60000 / dt))
            
            # Mozgóátlag frissítése
            self.rpm_history[self.history_index] = raw_rpm
            self.history_index = (self.history_index + 1) % config.MOVING_AVERAGE_SAMPLES
            
            # Átlagolás (0 értékeket is beleértve, ha a venti áll)
            self.current_rpm = int(sum(self.rpm_history) / len(self.rpm_history))
            
            # Stall detektálás
            if self.current_duty_percent > config.STALL_THRESHOLD_DUTY and self.current_rpm == 0:
                self.stall_detected = True
            else:
                self.stall_detected = False
                
            # Target RPM szabályozás (egyszerű feedback)
            if self.target_mode_active:
                self._adjust_for_target()

    def set_target_rpm(self, rpm):
        """Cél RPM beállítása."""
        self.target_rpm = rpm
        self.target_mode_active = True
        
    def disable_target_mode(self):
        self.target_mode_active = False

    def _adjust_for_target(self):
        """Egyszerű szabályozás a cél RPM eléréséhez."""
        if self.target_rpm <= 0:
            self.set_duty_percent(0)
            return

        error = self.target_rpm - self.current_rpm
        
        # Ha a hiba nagyobb mint a tűrés
        if abs(error) > config.TARGET_RPM_TOLERANCE:
            step = 1 if abs(error) < 500 else 5 # Dinamikus lépésköz
            if error > 0:
                self.set_duty_percent(self.current_duty_percent + step)
            else:
                self.set_duty_percent(self.current_duty_percent - step)

# Utolsó módosítás: 2026. február 05. 22:15:00