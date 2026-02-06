# Pandafix PWM 4-tűs ventilátor teszter

![Programnyelv](https://img.shields.io/badge/language-MicroPython-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20Pico-red.svg)
![Licenc](https://img.shields.io/badge/license-GPL--3.0-green.svg)

# README [EN/HU]
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/blob/master/README.md)
[![pt-br](https://img.shields.io/badge/lang-hu-green.svg)](https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/blob/master/README-HU.md)

Ez a projekt egy egyszerű, nyílt forráskódú megoldást kínál 4-tűs PWM ventilátorok tesztelésére Raspberry Pi Pico mikrovezérlő és SSD1306 OLED kijelző segítségével. Lehetővé teszi a ventilátor PWM munkaciklusának szabályozását és az RPM valós idejű monitorozását.

✨ **Funkciók**

*   **PWM Vezérlés:** Pontosan beállíthatja a ventilátor sebességét impulzusszélesség-moduláció (PWM) segítségével.
*   **Valós idejű RPM Megfigyelés:** Azonnali visszajelzést kap a ventilátor fordulatszámáról.
*   **OLED Kijelző Interfész:** Tiszta és tömör információk megjelenítése SSD1306 OLED képernyőn.
*   **Egyszerű firmware feltöltés:** Egyszerű „drag-and-drop” `.uf2` fájl feltöltés a gyors beállításhoz Raspberry Pi Pico-n.
*   **MicroPython Alapú:** Rugalmas és könnyen érthető kódbázis a testreszabáshoz.

📚 **Technológia**

*   **MicroPython:** Firmware beágyazott rendszerekhez, ideális a Raspberry Pi Pico-hoz.
*   **Raspberry Pi Pico (RP2040):** A projekt szíve, egy erőteljes és költséghatékony mikrovezérlő.
*   **SSD1306 OLED Kijelző:** Éles vizuális visszajelzéshez és felhasználói felületi elemekhez.
*   **PWM (impulzusszélesség-moduláció):** A ventilátor sebességének szabályozására szolgáló alapvető technológia.
*   **I2C Kommunikáció:** Az OLED kijelzővel való kommunikációhoz használatos.

🚀 **Telepítés**

A ventilátor teszter működéséhez kövesse az alábbi lépéseket:

1.  **Hardverkövetelmények:**
    *   Raspberry Pi Pico (vagy Pico W)
    *   4-tűs PWM ventilátor
    *   SSD1306 OLED kijelző (I2C 128x64 vagy 128x32)
    *   Jumper kábelek, próbapanel (opcionális prototípushoz)

2.  **Bekötés:**
    *   Csatlakoztassa az SSD1306 OLED kijelzőt a Raspberry Pi Pico-hoz I2C-n keresztül (SDA, SCL, VCC, GND).
    *   Csatlakoztassa a 4-tűs PWM ventilátort a Pico megfelelő GPIO-tűihez. Tekintse meg a `config.py` fájlt a pontos tűkiosztásért, ha forráskódból építi; egyébként használja a MicroPython szabványos PWM és RPM érzékelő tűit a Pico-n.

3.  **Firmware Feltöltés:**
    *   Töltse le a legújabb firmware `.uf2` fájlt (pl. `Pandafix-Fan-Tester-v2.uf2`) ebből a tárolóból.
    *   Nyomja meg és tartsa lenyomva a `BOOTSEL` gombot a Raspberry Pi Pico-n, majd csatlakoztassa a számítógéphez USB-kábellel. Engedje fel a `BOOTSEL` gombot, amint a Pico megjelenik tömegtároló eszközként (általában `RPI-RP2` néven).
    *   Húzza és ejtse a letöltött `.uf2` fájlt az `RPI-RP2` meghajtóra. A Pico automatikusan újraindul, és elindul a ventilátor teszter firmware-je.

▶️ **Használat**

A firmware telepítése és a hardver bekötése után:

1.  Kapcsolja be a Raspberry Pi Pico-t.
2.  Az OLED kijelző világítani fog, és megjeleníti az aktuális ventilátor állapotát, beleértve a beállított PWM munkaciklust és az érzékelt RPM-et.
3.  Használja a csatlakoztatott bemeneti gombokat (ha implementálva van, az `inputs.py` alapján) az opciók közötti navigáláshoz, a PWM munkaciklus beállításához, és figyelje a ventilátor sebességének és az RPM értékek változásait.

🤝 **Hozzájárulás**

A hozzájárulások teszik a nyílt forráskódú közösséget ilyen csodálatos hellyé a tanulásra, inspirációra és alkotásra. Bármilyen hozzájárulást **nagyra értékelünk**.

Ha van javaslata, ami jobbá tenné ezt a projektet, kérjük, forkolja a tárolót, és hozzon létre egy pull requestet. Egyszerűen nyithat egy hibajegyzetet is az „enhancement” címkével.

Fontolja meg a projekt vagy a fejlesztő támogatását:
*   GitHub: [@KonzolozZ](https://github.com/KonzolozZ)
*   Patreon: [pandafix](https://www.patreon.com/pandafix)
*   Buy Me a Coffee: [pandafix](https://www.buymeacoffee.com/pandafix)
*   PayPal: [Adományozás](https://www.paypal.com/donate/?hosted_button_id=7BRDHVYY98WK4)

📝 **Licenc**

GNU General Public License v3.0 alatt terjesztve. További információkért lásd a `LICENSE` fájlt.
