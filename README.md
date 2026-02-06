# Pandafix PWM 4-Pin Fan Tester

![Language](https://img.shields.io/badge/language-MicroPython-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20Pico-red.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)

# Multilanguage README Pattern
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/blob/master/README.md)
[![pt-br](https://img.shields.io/badge/lang-hu-green.svg)](https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/blob/master/README-HU.md)

This project provides a simple, open-source solution for testing 4-pin PWM fans using a Raspberry Pi Pico microcontroller and an SSD1306 OLED display. It allows you to control the fan's PWM duty cycle and monitor its RPM in real-time.

✨ **Features**

*   **PWM Control:** Precisely adjust the fan speed using Pulse Width Modulation.
*   **Real-time RPM Monitoring:** Get instant feedback on your fan's rotational speed.
*   **OLED Display Interface:** Clear and concise information displayed on an SSD1306 OLED screen.
*   **Easy Firmware Upload:** Simple drag-and-drop `.uf2` file upload for quick setup on Raspberry Pi Pico.
*   **MicroPython Based:** Flexible and easy to understand codebase for customization.

📚 **Tech Stack**

*   **MicroPython:** Firmware for embedded systems, ideal for Raspberry Pi Pico.
*   **Raspberry Pi Pico (RP2040):** The powerful and cost-effective microcontroller at the heart of the project.
*   **SSD1306 OLED Display:** For crisp visual feedback and user interface elements.
*   **PWM (Pulse Width Modulation):** The core technology for fan speed control.
*   **I2C Communication:** Used for communicating with the OLED display.

🚀 **Installation**

To get this fan tester up and running, follow these steps:

1.  **Hardware Requirements:**
    *   Raspberry Pi Pico (or Pico W)
    *   4-pin PWM Fan
    *   SSD1306 OLED Display (I2C 128x64 or 128x32)
    *   Jumper wires, breadboard (optional for prototyping)

2.  **Wiring:**
    *   Connect your SSD1306 OLED display to the Raspberry Pi Pico via I2C (SDA, SCL, VCC, GND).
    *   Connect the 4-pin PWM fan to the appropriate GPIO pins on the Pico. Refer to `config.py` for exact pin assignments if you're building from source; otherwise, use the standard PWM and RPM sense pins for MicroPython on Pico.

3.  **Firmware Upload:**
    *   Download the latest firmware `.uf2` file (e.g., `Pandafix-Fan-Tester-v2.uf2`) from this repository.
    *   Press and hold the `BOOTSEL` button on your Raspberry Pi Pico, then connect it to your computer using a USB cable. Release `BOOTSEL` once the Pico appears as a mass storage device (usually named `RPI-RP2`).
    *   Drag and drop the downloaded `.uf2` file onto the `RPI-RP2` drive. The Pico will automatically reboot, and the fan tester firmware will start.

▶️ **Usage**

Once the firmware is installed and the hardware is wired:

1.  Power up your Raspberry Pi Pico.
2.  The OLED display will light up and show the current fan status, including the set PWM duty cycle and the detected RPM.
3.  Use the connected input buttons (if implemented, as inferred from `inputs.py`) to navigate through options, adjust the PWM duty cycle, and observe changes in fan speed and RPM readings.

🤝 **Contributing**

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Consider supporting the project or the developer:
*   GitHub: [@KonzolozZ](https://github.com/KonzolozZ)
*   Patreon: [pandafix](https://www.patreon.com/pandafix)
*   Buy Me a Coffee: [pandafix](https://www.buymeacoffee.com/pandafix)
*   PayPal: [Donate](https://www.paypal.com/donate/?hosted_button_id=7BRDHVYY98WK4)

📝 **License**

Distributed under the GNU General Public License v3.0. See `LICENSE` for more information.
