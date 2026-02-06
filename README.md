# 🌈✨ Pandafix PWM 4-Pin Fan Tester ✨🌈

<!-- Badges -->
![MicroPython](https://img.shields.io/badge/MicroPython-Python-blue.svg?logo=python)
![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20Pico-orange.svg?logo=raspberrypi)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/KonzolozZ/pandafix-pwm-4pin-fan-tester/build_firmware.yml?branch=main)](https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/actions/workflows/build_firmware.yml)
[![Patreon](https://img.shields.io/badge/Patreon-Support-orange?logo=patreon&labelColor=lightgrey)](https://www.patreon.com/pandafix)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-FFDD00?logo=buy-me-a-coffee&labelColor=lightgrey)](https://www.buymeacoffee.com/pandafix)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue?logo=paypal&labelColor=lightgrey)](https://www.paypal.com/donate/?hosted_button_id=7BRDHVYY98WK4)

<div align="center">
  <a href="https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/assets/your_video_link_here"> <!-- Placeholder: Replace with actual video link if available -->
    <img src=".github/pandafix-fan-tester-test-module.jpg" alt="Pandafix Fan Tester in action" width="600"/>
  </a>
  <br/>
  _Click the image to watch a demo! (Please replace link with actual video URL)_
</div>

---

## 📝 Description

The **Pandafix PWM 4-Pin Fan Tester** is a powerful and user-friendly MicroPython-based device designed for the Raspberry Pi Pico, dedicated to testing and monitoring 4-pin PC PWM fans. It provides comprehensive control over fan speed and precise RPM measurement, all displayed on a crisp OLED screen. With multiple testing modes (including automatic, manual, and target RPM control), configurable settings, multi-language support, and built-in safety features, this project is an invaluable tool for hardware enthusiasts, PC builders, and technicians to quickly assess fan performance and identify issues like stalling.

---

## ✨ Features

*   **Universal PWM Fan Control:** Seamlessly control any standard 4-pin PC PWM fan (12V, standard pinout).
*   **Precise RPM Measurement:** Get accurate fan speed readings with a moving average calculation, shown live on the display.
*   **Intuitive OLED Display:** A compact 128x32 SSD1306 OLED screen provides clear information with animated menus and status updates.
*   **Multiple Test Modes:**
    *   **Auto Test:** Automatically cycles through a predefined PWM range (e.g., 0-100%) at set intervals.
    *   **Manual Test:** Allows manual stepping of PWM percentage with adjustable step sizes.
    *   **Target RPM Mode:** Utilizes a PID-like control to actively maintain a specific target RPM. Cycle through target RPM presets.
*   **Multilanguage Support:** Choose your preferred interface language from English, Hungarian, German, Spanish, French, and Italian, switchable on-the-fly.
*   **Configurable Settings:** Adjust PWM step size, button debounce sensitivity, and language directly from the device menu.
*   **Smart Safety:** Features fan stall detection (alerts if RPM is 0 above a certain PWM threshold) and real-time monitoring of the internal RP2040 temperature.
*   **Two-Button Navigation:** Simple and effective control with dedicated Menu (`B`) and Select (`A`) buttons.
*   **Modular MicroPython Codebase:** Clean, object-oriented programming (OOP) structure using `uasyncio` for responsive, non-blocking operation.

---

## 📚 Tech Stack

*   **Microcontroller:** Raspberry Pi Pico (RP2040)
*   **Programming Language:** MicroPython
*   **Display:** SSD1306 OLED (128x32 pixels)
*   **Communication:** I2C (for OLED display)
*   **Peripherals:** PWM (Pulse Width Modulation), GPIO (for buttons and TACH signal), ADC (for internal temperature sensor)
*   **Libraries:** `uasyncio` (for asynchronous operations and responsive UI/background tasks)

---

## 🚀 Installation

There are two primary ways to get the Pandafix Fan Tester running on your Raspberry Pi Pico: by flashing a pre-built firmware (`.uf2`) or by uploading the individual MicroPython source files.

### Option 1: Flash Pre-built Firmware (Recommended)

1.  **Download the `.uf2` file:** Obtain the latest `Pandafix-Fan-Tester-v2.uf2` file from the [releases page](https://github.com/KonzolozZ/pandafix-pwm-4pin-fan-tester/releases) or the project root.
2.  **Enter BOOTSEL mode:**
    *   **Hold down** the <kbd>BOOTSEL</kbd> button on your Raspberry Pi Pico.
    *   **Plug** your Pico into your computer's USB port while still holding <kbd>BOOTSEL</kbd>.
    *   Release <kbd>BOOTSEL</kbd> once a new removable drive named `RPI-RP2` appears on your computer.
3.  **Copy the firmware:** Drag and drop the downloaded `Pandafix-Fan-Tester-v2.uf2` file onto the `RPI-RP2` drive.
4.  The Pico will automatically reboot, and the fan tester application will start.

### Option 2: Upload MicroPython Source Files (for Development/Customization)

This method is ideal for developers who want to modify the code or deploy a custom MicroPython build.

1.  **Install MicroPython Firmware:** If your Pico doesn't already have MicroPython installed, download the official MicroPython `.uf2` firmware for Raspberry Pi Pico from [MicroPython.org](https://micropython.org/download/rp2-pico/). Follow the BOOTSEL flashing steps above to install it.
2.  **Install Thonny IDE:** Thonny is a beginner-friendly Python IDE that works well with MicroPython. Download and install it from [thonny.org](https://thonny.org/).
3.  **Connect Pico to Thonny:**
    *   Open Thonny.
    *   Go to `Run` > `Select interpreter...`.
    *   Choose `MicroPython (Raspberry Pi Pico)` and select the correct port.
4.  **Copy Project Files:** Copy all `.py` files from the project root directory (e.g., `config.py`, `fan_control.py`, `inputs.py`, `locales.py`, `main.py`, `settings_manager.py`, `ssd1306.py`, `ui_display.py`) to the root of your Pico's filesystem using Thonny's file manager.
5.  **Reboot Pico:** Once all files are copied, soft reboot your Pico (e.g., by clicking the green "Run" button in Thonny or unplugging/replugging). The `main.py` script will automatically execute.

### 🔌 Hardware Wiring

The device requires an OLED display and two buttons, along with a 4-pin fan. **Crucially, the fan's 12V power must come from an *external* power supply! Ensure all grounds are connected together.**

| Function            | Pico GPIO | Connects to                                      |
| :------------------ | :-------- | :----------------------------------------------- |
| PWM output          | `GP16`    | Fan PWM (typically blue wire)                    |
| TACH input          | `GP17`    | Fan TACH (typically yellow wire) **+1Kohm pull-up resistor** to 3.3V |
| Menu button (B)     | `GP14`    | Button to GND                                    |
| Select button (A)   | `GP15`    | Button to GND                                    |
| OLED SDA            | `GP4`     | OLED I2C SDA                                     |
| OLED SCL            | `GP5`     | OLED I2C SCL                                     |
| OLED VCC            | `3V3`     | OLED Power (from Pico 3.3V out)                  |
| OLED GND            | `GND`     | OLED/Fan/Buttons GND                             |

---

## ▶️ Usage

The Pandafix Fan Tester features a simple two-button interface for navigation and control.

### Controls

*   <kbd>B</kbd> (Menu button - `GP14`):
    *   In menus: Cycles through available menu options.
    *   In test modes: Returns to the main menu or the previous screen.
*   <kbd>A</kbd> (Select button - `GP15`):
    *   In menus: Enters the selected mode or option.
    *   In `MANUAL TEST` mode: Steps up the fan's PWM percentage.
    *   In `TARGET RPM` mode: Cycles through predefined target RPM values.
    *   In settings: Confirms a selection and saves it.

### Modes and Options

*   **`AUTO TEST`**: The fan will automatically cycle through predefined PWM percentages (e.g., 0%, 20%, 40%, ..., 100%) at set intervals (configured in `config.py`).
*   **`MANUAL TEST`**: Manually adjust the fan's PWM duty cycle. Press the <kbd>A</kbd> button to increment the PWM percentage. The step size can be configured in the settings.
*   **`TARGET RPM`**: Set a specific RPM value. The device will dynamically adjust the PWM to attempt to hold the fan at this target speed using a PID-like control loop. Use <kbd>A</kbd> to cycle through target RPM presets.
*   **`SETTINGS`**: Access the configuration menu:
    *   **`LANGUAGE SELECT`**: Choose your preferred interface language from the supported options.
    *   **`PWM STEP SIZE`**: Adjust the increment/decrement value for manual PWM control (e.g., 5%, 10%, 20%, 25%).
    *   **`BUTTON SENSITIVITY`**: Configure the debounce time (in milliseconds) for the buttons, useful for preventing multiple presses from a single physical button press.
*   **`ABOUT`**: Displays project information, credits, and features with a "Star Wars"-style scrolling text animation.

---

## 🤝 Contributing

We welcome contributions to improve the Pandafix Fan Tester! If you have suggestions for features, bug fixes, or new language translations, please feel free to:

1.  **Fork** the repository.
2.  **Create** a new branch (`git checkout -b feature/AmazingFeature`).
3.  **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
4.  **Push** to the branch (`git push origin feature/AmazingFeature`).
5.  **Open a Pull Request**.

For major changes, please open an issue first to discuss what you would like to change.

Consider supporting the project via the [Patreon](https://www.patreon.com/pandafix), [Buy Me A Coffee](https://www.buymeacoffee.com/pandafix), or [PayPal](https://www.paypal.com/donate/?hosted_button_id=7BRDHVYY98WK4) funding options if you find it useful!

---

## 📝 License

This project is distributed under the **GNU GENERAL PUBLIC LICENSE Version 3**. See the `LICENSE` file for more information.

---