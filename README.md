# 🌡️ Kobra X Dynamic Bed Heating Ramp

A smart Python post-processing script for **Orca Slicer**, designed specifically for the **Anycubic Kobra X** (via KX-Bridge). 

This script dynamically generates a stepped heating ramp for the printer bed *before* the main start macro executes. It reads the current bed temperature directly from the printer, preventing massive power spikes (saving your UPS from overload) and automatically skipping unnecessary heating steps if the bed is already warm from a previous print.

> ⚠️ **Important Note on UPS Compatibility:** 
> This script is specifically designed for UPS systems that signal an overload with an audible alarm (beeping) but do not immediately cut power. It has **not** been tested with UPS units that instantly disconnect the power supply upon overload. However, using very small ramp increments (e.g., `RAMP_STEP=5` or lower) might successfully prevent power cuts on those stricter UPS models.
>
> 
## ✨ Features
- **Dynamic Stepping**: Automatically calculates heating steps based on your desired temperature increment (e.g., every 10°C).
- **Smart Skip**: If the bed is already at or above a target step temperature, that step is automatically skipped, saving time on consecutive prints.
- **Direct Mode**: Set the step to `0` to bypass the ramp and heat directly to the target temperature.
- **Clean G-code**: Intelligently injects the ramp right before the `G9111` macro and neatly organizes comments.
- **Safe Fallback**: If the bridge is unreachable, it safely defaults to a standard cold-start ramp without breaking the slice.

## 📋 Requirements
1. **Orca Slicer** (any recent version supporting Post-Processing Scripts).
2. **[KX-Bridge](https://gitea.it-drui.de/viewit/KX-Bridge-Release)** running and accessible on your local network.
3. **Python**: No separate installation required! You can use the Python executable already bundled inside the Orca Slicer installation directory.

## ⚙️ Installation & Configuration

### Step 1: Configure the Script
1. Download `ramp_bed_heating.py`.
2. Open the file in a text editor.
3. **Crucial**: Modify the `BRIDGE_BASE_URL` variable at the top of the script to match your KX-Bridge IP address and port:

    BRIDGE_BASE_URL = "http://192.168.xxx.xxx:7125" 

4. Save the file in a permanent location on your computer.

### Step 2: Add to Orca Slicer
1. Open Orca Slicer and go to **Preset Settings** -> **Others** tab.
2. Find the **Post-Processing Scripts** field.
3. Add the path to the **bundled Orca Slicer Python executable** followed by the path to the script. For example:

    Windows:
    "C:\Program Files\OrcaSlicer\python\python.exe" "C:\Path\To\ramp_bed_heating.py"

    macOS/Linux:
    /Applications/OrcaSlicer.app/Contents/Resources/python/bin/python3 "/path/to/ramp_bed_heating.py"

    *(Note: If the bundled path does not work, you can install the latest official Python version from [python.org](https://www.python.org/downloads/). After installation, open your command prompt or terminal and type `where python` (Windows) or `which python3` (macOS/Linux) to find the correct executable path. Remember to use quotes `"` around paths that contain spaces).*

### Step 3: Configure your Start G-code
In your Printer's **Machine G-code** (Start G-code), add the `RAMP_STEP` variable anywhere before the `G9111` macro:

    ; RAMP_STEP=10
    ; (Rest of your custom start G-code...)
    G9111 bedTemp=[first_layer_bed_temperature] extruderTemp=[first_layer_temperature]

## 🚀 How to Use RAMP_STEP
You can control the heating behavior by changing the number in the `; RAMP_STEP=X` comment in your Start G-code:

- `; RAMP_STEP=10` (Recommended): Heats the bed in 10°C increments. Best balance between UPS protection and speed.
- `; RAMP_STEP=5`: Finer 5°C increments. Ideal for very sensitive UPS systems or high-temp materials.
- `; RAMP_STEP=0`: **Bypass mode**. Disables the ramp and heats directly to the target temperature (useful for low-temp PLA or when UPS load is not a concern).

## 🙏 Credits & Acknowledgments
This script would not be possible without the incredible reverse-engineering and development work done by **viewit** on the [KX-Bridge](https://gitea.it-drui.de/viewit/KX-Bridge-Release) project. A huge thank you for providing the local API that makes this smart automation possible!

## 📜 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---
*Disclaimer: This script is provided "as is". Always monitor your first few prints when introducing new G-code modifications to ensure your specific hardware setup behaves as expected.*
