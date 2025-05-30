![Top Banner](https://github.com/user-attachments/assets/7fda2d74-d90f-4a15-a4f0-2e73835bf580)
# LeapGlove Project

## Overview
The **LeapGlove Project** aims to repurpose the [LucidGloves](https://github.com/LucidVR/lucidgloves) to control the [LeapHand](https://v1.leaphand.com/) while retaining the haptic feedback capabilities of the glove. 

This initiative focuses on creating an affordable, human-computer interaction interface for the LeapHand. 

---

## Objectives
- Repurpose the LucidGloves to function as controllers for the LeapHand.
- Retain the haptic feedback features of the LucidGloves.
- Provide an affordable and accessible solution for LeapHand control.

---

## Project Status
This project is currently in development. Progress updates, detailed documentation, and additional resources will be provided as they become available.

---

## Sources
The LeapGlove Project builds on:

- **LucidGloves Prototype 4**: [GitHub Repository](https://github.com/LucidVR/lucidgloves)
- **LeapHand API**: [LeapHand Documentation](https://v1.leaphand.com/)

---

## How to Build the LeapGlove

### 3D Printing & Parts

- **Find the STL files:**  
  Navigate to the `lucidglove/3d models` folder in this repository to locate all the required printable parts.  
  > **Note:** Some models differ from the original LucidGlove designs, featuring improvements for print quality and structural strength.

- **Check the README in each subfolder:**  
  Each subfolder contains a `README` file specifying which parts to print and how many of each are needed.

- **Printing Tips:**  
  - Use PLA or PETG for strength and reliability.
  - Recommended infill: at least 20% for durability.
  - Some parts may require supports (snug supports are recommended for all the sliding parts. For the rest use snug supports).
  - Test-fit parts before final assembly.

- **Assembly Notes:**  
  - The majority of the glove’s assembly follows the original LucidGlove design.  
  - The haptic modules are designed to be hot-glued into place; use hot glue for a secure fit if needed.
  - Wiring should follow the LucidGlove repository guidelines for sensor and ESP32 placement.

- **Differences from Original:**  
  - Improved models for easier printing and stronger construction.
  - Some tweaks for better fitment of electronics and servos.
    

### Final Steps

- **Firmware:**  
  Flash our version of the LucidGlove firmware to your ESP32 as described in the [LucidGlove instructions](https://github.com/LucidVR/lucidgloves).

- **LeapHand Setup:**  
  Build and connect the LeapHand to your PC following the [LeapHand documentation](https://v1.leaphand.com/).

- **Software:**  
  Once hardware is ready and connected (if used bluetooth dont forget to pair to the LeapGlove), run the integration script for the `Our Files` Folder:
  ```bash
  python leapglove.py

### Demonstration Videos
- **Glove Demo**:

https://github.com/user-attachments/assets/84f64e34-5cb0-47a1-a268-5b9e06becb94

- **Leap Hand Demo (Courtesy of LeapHand.com)**:

  https://github.com/user-attachments/assets/7a54c01e-ebf4-48aa-9cdf-c213115a098e

- ** LeapGlove Final Demo**:

  [paste link here later]

---


## Contact
For any questions, suggestions, or collaboration opportunities, feel free to reach out:
- **Email**: zuabiamir@gmail.com

![Bottom Banner](https://github.com/user-attachments/assets/37fdd0cc-1e97-464d-82f6-6b3a6e116ac4)
