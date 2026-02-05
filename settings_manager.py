# Fájl helye: /settings_manager.py
# Funkció: A felhasználói beállítások (pl. nyelv) perzisztens tárolása JSON fájlban.

import json
import os
import config

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = {
            "language": config.DEFAULT_LANGUAGE
        }
        self.load()

    def load(self):
        """Beállítások betöltése fájlból."""
        try:
            # Ellenőrizzük, hogy létezik-e a fájl
            try:
                os.stat(self.filename)
            except OSError:
                return # Fájl nem létezik, maradnak az alapértelmezések

            with open(self.filename, "r") as f:
                data = json.load(f)
                # Csak azokat a kulcsokat frissítjük, amik léteznek a defaults-ban,
                # vagy bővítjük, ha szükséges.
                if data:
                    self.settings.update(data)
                    if config.DEBUG_MODE:
                        print(f"Beállítások betöltve: {self.settings}")
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Hiba a beállítások betöltésekor: {e}")

    def save(self):
        """Beállítások mentése fájlba."""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.settings, f)
            if config.DEBUG_MODE:
                print(f"Beállítások mentve: {self.settings}")
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Hiba a beállítások mentésekor: {e}")

    def get(self, key):
        """Beállítás lekérdezése."""
        return self.settings.get(key)

    def set(self, key, value):
        """Beállítás módosítása és mentése."""
        self.settings[key] = value
        self.save()

# Utolsó módosítás: 2026. február 05. 22:20:00