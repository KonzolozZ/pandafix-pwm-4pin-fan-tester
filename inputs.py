# Fájl helye: /inputs.py
# Funkció: Gombok kezelése aszinkron módon, pergésmentesítéssel (debounce).

from machine import Pin
import uasyncio as asyncio
import time

class Button:
    def __init__(self, pin_num, callback, debounce_ms=200):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.callback = callback
        self.debounce_ms = debounce_ms
        self.last_press_time = 0
        self._is_pressed = False
        
        # Háttérfolyamat indítása a gomb figyelésére
        asyncio.create_task(self._monitor())

    async def _monitor(self):
        while True:
            current_val = self.pin.value()
            
            # Aktív alacsony (PULL_UP miatt 0 ha lenyomva)
            if current_val == 0:
                now = time.ticks_ms()
                if not self._is_pressed and time.ticks_diff(now, self.last_press_time) > self.debounce_ms:
                    self.last_press_time = now
                    self._is_pressed = True
                    if self.callback:
                        self.callback() # Callback hívása
            else:
                self._is_pressed = False
                
            await asyncio.sleep_ms(20) # Poll interval

# Utolsó módosítás: 2026. február 05. 22:15:00