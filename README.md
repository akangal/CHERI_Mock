# CHERI Educational Mock Model 🌕🤖

# CHERI Educational Mock Model 🌕🤖

An open-source, 60% scale educational and hobbyist replica of the CHERI (Challenging Environment Exploration Robot for Intelligence) lunar rover, originally developed for Türkiye's first lunar rover project in the Chang'e 8 mission at METU (Middle East Technical University). 

This repository contains everything you need to build your own scaled-down CHERI rover. The chassis is designed to be accessible and easily manufactured, utilizing a 3mm plexiglass "puzzle" assembly method reinforced with 3D-printed corner mounts (or adhesive). It is driven by a Raspberry Pi Pico W, acting as a standalone Wi-Fi hotspot for remote control from any smart device.

## ✨ Features
* **Accessible Chassis Design:** Cut from standard 3mm plexiglass with interlocking puzzle-like joints.
* **Reinforced Assembly:** Includes 3D printable corner mounts for enhanced structural integrity.
* **Standalone Wi-Fi Control:** The Raspberry Pi Pico acts as its own Access Point (AP), meaning you don't need a local router to connect and control the rover.
* **Interactive Sensors & Feedback:** * Front-facing LEDs for illumination.
  * PIR sensor for motion detection.
  * Onboard buzzer for generating robotic "emotion" sounds.
* **Accurate Locomotion:** Designed to accommodate the project's signature J-shaped whegs.

## 📂 Repository Structure
* `/cad` - 2D cut drawings (DXF) for the 3mm plexiglass and 3D print files (STL/STEP) for the corner mounts.
* `/docs` - Renderings, photos of the completed build, and step-by-step assembly instructions.
* `/electronics` - Wiring diagrams, pinouts, and the complete Bill of Materials (BOM).
* `/src` - MicroPython code for the Raspberry Pi Pico.

## 🚀 Getting Started
1. **Fabrication:** Laser cut the plexiglass files located in the `/cad` folder and 3D print the corner mounts. 
2. **Assembly:** Follow the visual guide in `/docs/assembly_instructions.md` to piece together the chassis.
3. **Wiring:** Connect the Pico, motor drivers, PIR sensor, LEDs, and buzzer according to the schematic in `/electronics`.
4. **Firmware:** Flash your Raspberry Pi Pico with MicroPython and upload the scripts from the `/src` folder.
5. **Connect & Drive:** Power up the rover, connect your phone or laptop to the "CHERI_Rover" Wi-Fi network, and open the control interface in your web browser.

## 👤 Author
**Ahmet M. Kangal** * [LinkedIn](https://www.linkedin.com/in/ahmet-mustafa-kangal/)
