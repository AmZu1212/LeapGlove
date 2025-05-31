![Top Banner](https://github.com/user-attachments/assets/7fda2d74-d90f-4a15-a4f0-2e73835bf580)
<div align="center">
  <h1>The LeapGlove Project</h1>
  <img src="https://github.com/user-attachments/assets/d99663a5-5f14-471e-bad9-8e396a9287bb" alt="LeapGlove" width="600"/>
</div>

## Contact Us
For any questions, feel free to reach out:
- **Emails**: zuabiamir@gmail.com , liz.dushkin@gmail.com
  
## Overview
The **LeapGlove Project** aims to repurpose the [LucidGloves](https://github.com/LucidVR/lucidgloves) to control the [LeapHand](https://v1.leaphand.com/) while retaining the haptic feedback capabilities of the glove. 

This initiative focuses on creating an affordable, human-computer interaction interface for the LeapHand. 

The LeapGlove Project builds on:
- **LucidGloves Prototype 4**: [GitHub Repository](https://github.com/LucidVR/lucidgloves)
- **LeapHand API**: [LeapHand Documentation](https://v1.leaphand.com/)

please consider leaving a star on both of the repos above, as without their previous work, this would not be possible.

---

## Project Objectives
- Repurpose the LucidGloves to function as controllers for the LeapHand.
- Retain the haptic feedback features of the LucidGloves.
- Provide an affordable and accessible solution for LeapHand control.

---

## Project Status
This project is finished. Unfortunately we fell abit short of our expected implementation due to the physical design of the mechanism, and due to the latency the servo motors have.
As a leap hand controller, the gloves supports general finger motion, except fine grain movement and splay movement. And for the hapttiic, it was unfortunaetely impossible to implement a realtime transmition of haptics, so we created haptic presets from 0% to 90%, so it can be demo'ed if anyone wishes to see how it may feel. 

---

## LeapGlove Assembly & Setup Guide

## Step 1: Complete Hardware List
The hardware needed is listed here, or alternatively you can check lucas'es hadrware list. 
Just be sure to use an `esp32-wroom-32` and not an arduino nano. [Lucas's original parts list](https://github.com/LucidVR/lucidgloves/wiki/Prototype-4-Parts-List)

The Required Hardware:
- 5 black badge reels
- 5 round 10k potentiometers
- 5 mg90s 9g servos
- 1 ESP32-WROOM-32
- 2 small powerbanks (or a power solution of your choice)
- 1 firm-cloth glove (**cloth should not be flexible** for proper haptics)
- Dupont crimp set, crimper, and 28AWG wire kit
- 2 USB-C cables (one for ESP32, one for servos)
- 1 spool of standard PLA/PETG for 3D printing (and a 3D printer)
- 4 M2 bolts and nuts
- Soldering iron and solder
- Foam surface for comfort (to stick under the motor mount base)
- Hot glue gun (even a cheap one will do)
- Some small rope
- A Scotch fishing strap 

> **You will also need a LeapHand already built. See:**  
> [LeapHand Website & CAD Files](https://v1.leaphand.com/leap_cad)


## Step 2: 3D Printing Guide

- Please follow the guide below:  
  [Prototype 4 Printing Guide](https://github.com/LucidVR/lucidgloves/wiki/Prototype-4-Printing-Guide)

- Find the STL files: 
  Navigate to the `lucidglove/3d models` folder in this repository to locate all the required printable parts.  
  > **Note:** Some models differ from the original LucidGlove designs, featuring improvements for print quality and structural strength.

- Check the README in each subfolder:
  Each subfolder contains a `README` file specifying which parts to print and how many of each are needed.

- **Printing Tips:**  
  - Use PLA or PETG for strength and reliability.
  - Recommended infill: at least 20% for durability.
  - Some parts may require supports (snug supports are recommended for all the sliding parts. For the rest use *snug* supports).
  - Test-fit parts before final assembly.


## Step 3: Assembly

Refer to Lucas’s video for a step-by-step assembly:  
[![Assembly Video](https://img.youtube.com/vi/2yF-SJcg3zQ/0.jpg)](https://www.youtube.com/watch?v=2yF-SJcg3zQ)

**Notes:**
- The majority of the glove’s assembly follows the original LucidGlove design.  
- Use the .stl files we provided (they are more print-friendly than Lucas's designs).
- The motor mounts are designed to be hot glued onto the glove (there is extra space to glue under and on the sides).
- Instead of mounting a Quest2 controller, use the ESP32 mount we provided.


## Step 4: ESP32 Connections

There is flexibility in pin choice if you edit the firmware config.  
This guide assumes you are using the provided firmware as-is (we recommend to not change anything and run as-is).

- The wires should be connected like so:
  ![image](https://github.com/user-attachments/assets/75371a49-d9d7-43d0-9198-98732fd23504)
- The finished product should look like this:
  ![image](https://github.com/user-attachments/assets/80aee6a9-6791-43b3-a583-a5de7836cbba)
  
## Step 5: Setting Up the Code

1. **Download CH340 USB drivers:**  
   - [CH340 driver link here](https://sparks.gogo.co.nz/ch340.html)
   - please not that maybe your esp wil have a cp210 driver instead, just install that one.
   - The driver type depends on the small chip near the usb port on the esp board.

2. **Install drivers** and connect your ESP32 board via USB.

3. **Open Windows Device Manager:**
    - Right click the Windows icon  
      ![image](https://github.com/user-attachments/assets/6019bdc2-e071-4d57-8937-a9393a27cb97)
    - Choose Device Manager  
      ![image](https://github.com/user-attachments/assets/1de04038-150e-40af-8ba3-ef86dca4d41b)

    - Find your “CH340” COM device under Ports (COM & LPT). (For us it is COM3, but for you the number may be different) 
      ![image](https://github.com/user-attachments/assets/55b58ef7-0c26-415d-a2d3-3532c8f96fde)

4. **Download and install Arduino IDE.**  
   Follow Lucas’s video for preparation and board profile setup (use the updated firmware):  
   [Lucas's Arduino Prep Video](https://www.youtube.com/watch?v=2yF-SJcg3zQ)

5. **Compile and program the ESP32.**

6. **Connect the electronics and pair the LeapGlove with Windows via Bluetooth:**
    - Open your PC’s Bluetooth panel and pair with the LeapGlove.
    - Check in device manager which COM# is your esp bluetooth connection:

      ![image](https://github.com/user-attachments/assets/9f4184cc-f68d-4b25-a4c3-11a6e81f580e)
      
    - Update the esp port in the script:
      ![image](https://github.com/user-attachments/assets/d08bcf45-913b-4b04-b0b3-2f612205aaf6)

## Step 6: How to Wear and Use the Glove Safely

- **Tension will differ per user.**
- **You must:**  
  - Re-tighten the ropes  
  - Adjust the servo motor’s tail

### Rope and Servo Adjustment Procedure

1. Remove all 5 tails from the servos.
2. Run the script, press `Ctrl+C`, and wait for calibration to finish.
3. Press `0` to reset servo positions to zero.  
   Close the script.
4. Tighten and spin the ropes on each finger cap handle.
    - Ensure there is tension even when the hand is fully open.
5. Close your hand.
6. For each motor, one by one, put the tail on **after** (clockwise) the screw position.  
   This sets the motor’s “zero” point. Please refer to the image and gif below:
   <img src="https://github.com/user-attachments/assets/b3c7d500-4104-4469-a516-5af31faa5246" alt="Motor Tail Placement" width="300"/>
   
   GIF of how it should look like:
   <img src="https://github.com/user-attachments/assets/e2f44b70-f850-4cbf-b12a-898178204774" alt="Motor Tail Placement GIF" width="300"/>



### Operation Safety

- **Always have your hand fully open when changing haptic presets.**  
  - Not doing so may cause the servo tail to hit the brake screw and dislodge it, ruining the haptic mechanism.
- **If you have tracking issues:**  
  - Ropes aren’t tight enough. Re-tighten and recalibrate.
- **If you have haptics issues (servos don’t stop hand movement):**  
  - Glove material is too flexible, or servos are misaligned. Re-align as above.

### Final Steps

- **LeapHand Setup:**  
  Build and connect the LeapHand to your PC following the [LeapHand documentation](https://v1.leaphand.com/).

- **Software:**  
  Once hardware is ready and connected (if used bluetooth dont forget to pair to the LeapGlove), run the integration script for the `Our Files` Folder:
  ```
  python leapglove.py
  ```

### Demonstration Videos
- **Glove Demo**:

https://github.com/user-attachments/assets/84f64e34-5cb0-47a1-a268-5b9e06becb94

- **Leap Hand Demo (Courtesy of LeapHand.com)**:

https://github.com/user-attachments/assets/7a54c01e-ebf4-48aa-9cdf-c213115a098e

- ** LeapGlove Final Demo**:

  [paste link here later]

---

![Bottom Banner](https://github.com/user-attachments/assets/37fdd0cc-1e97-464d-82f6-6b3a6e116ac4)
