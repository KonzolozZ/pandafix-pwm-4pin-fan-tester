# Fájl helye: /locales.py
# Funkció: A rendszer összes támogatott nyelvi fordításának tárolása.

LOCALES = {
    "en": {
        "app_name": "Pandafix",
        "app_sub": "Fan Tester",
        "init_hw": "HW Init...",
        "error_init": "Init Error!",
        "menu_title": "SELECT MODE",
        "mode_auto": "AUTO TEST",
        "mode_manual": "MANUAL TEST",
        "mode_target": "TARGET RPM",
        "mode_language": "LANGUAGE",
        "pwm": "PWM",
        "rpm": "RPM",
        "target": "TGT",
        "temp": "Temp",
        "stall_alert": "ERROR! (STALL)",
        "btn_nav": "A:Select B:Menu",
        "btn_back": "B: Back",
        "saved": "Saved!",
        "lang_name": "English"
    },
    "hu": {
        "app_name": "Pandafix",
        "app_sub": "Fan Tester",
        "init_hw": "Hardver init...",
        "error_init": "Init hiba!",
        "menu_title": "MOD VALASZTAS",
        "mode_auto": "AUTO TESZT",
        "mode_manual": "KEZI TESZT",
        "mode_target": "CEL RPM",
        "mode_language": "NYELV / LANG",
        "pwm": "PWM",
        "rpm": "RPM",
        "target": "CEL",
        "temp": "Hom.",
        "stall_alert": "HIBA! (STALL)",
        "btn_nav": "A:Valaszt B:Menu",
        "btn_back": "B: Vissza",
        "saved": "Mentve!",
        "lang_name": "Magyar"
    },
    "de": {
        "app_name": "Pandafix",
        "app_sub": "Luefter Test",
        "init_hw": "HW Init...",
        "error_init": "Init Fehler!",
        "menu_title": "MODUS WAEHLEN",
        "mode_auto": "AUTO TEST",
        "mode_manual": "MANUELL",
        "mode_target": "ZIEL RPM",
        "mode_language": "SPRACHE",
        "pwm": "PWM",
        "rpm": "RPM",
        "target": "ZIEL",
        "temp": "Temp",
        "stall_alert": "FEHLER! (STALL)",
        "btn_nav": "A:Wahl B:Menu",
        "btn_back": "B: Zurueck",
        "saved": "Gesp.!",
        "lang_name": "Deutsch"
    },
    "es": {
        "app_name": "Pandafix",
        "app_sub": "Fan Tester",
        "init_hw": "Inic. HW...",
        "error_init": "Error Init!",
        "menu_title": "SELECC. MODO",
        "mode_auto": "AUTO TEST",
        "mode_manual": "MANUAL",
        "mode_target": "RPM OBJ.",
        "mode_language": "IDIOMA",
        "pwm": "PWM",
        "rpm": "RPM",
        "target": "OBJ",
        "temp": "Temp",
        "stall_alert": "ERROR! (STALL)",
        "btn_nav": "A:Sel B:Menu",
        "btn_back": "B: Atras",
        "saved": "Guard.!",
        "lang_name": "Espanol"
    },
    "fr": {
        "app_name": "Pandafix",
        "app_sub": "Testeur Vent.",
        "init_hw": "Init Mat...",
        "error_init": "Erreur Init!",
        "menu_title": "MODE",
        "mode_auto": "TEST AUTO",
        "mode_manual": "MANUEL",
        "mode_target": "CIBLE RPM",
        "mode_language": "LANGUE",
        "pwm": "PWM",
        "rpm": "RPM",
        "target": "CIBL",
        "temp": "Temp",
        "stall_alert": "ERREUR (STALL)",
        "btn_nav": "A:Sel B:Menu",
        "btn_back": "B: Retour",
        "saved": "Enreg.!",
        "lang_name": "Francais"
    },
    "it": {
        "app_name": "Pandafix",
        "app_sub": "Fan Tester",
        "init_hw": "Init HW...",
        "error_init": "Errore Init!",
        "menu_title": "MODALITA",
        "mode_auto": "TEST AUTO",
        "mode_manual": "MANUALE",
        "mode_target": "TARGET RPM",
        "mode_language": "LINGUA",
        "pwm": "PWM",
        "rpm": "RPM",
        "target": "OBIET",
        "temp": "Temp",
        "stall_alert": "ERRORE (STALL)",
        "btn_nav": "A:Sel B:Menu",
        "btn_back": "B: Indietro",
        "saved": "Salv.!",
        "lang_name": "Italiano"
    }
}

def get_locale(lang_code):
    """Visszaadja a kért nyelv szótárát, vagy az alapértelmezettet ha nem létezik."""
    if lang_code in LOCALES:
        return LOCALES[lang_code]
    return LOCALES["en"] # Fallback

# Utolsó módosítás: 2026. február 05. 22:20:00