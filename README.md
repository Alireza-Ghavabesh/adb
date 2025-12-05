# Android VPN for Windows via ADB

## ⭐ Use Your Android's VPN on Your Windows PC ⭐

This project allows you to route your Windows internet traffic through an Android emulator's VPN connection. By using an Android emulator and the EveryProxy app, this tool forwards the connection from the emulator to your local machine, allowing any application on your PC to use the VPN.

<img src="./adb.png" alt="Project Banner">

## Features

- **Easy to Use**: A simple `emuVPN.exe` watchdog handles the connection automatically.
- **Stable Connection**: The script continuously monitors the ADB connection and proxy health, resetting it if it fails.
- **System-Wide VPN**: Route any Windows application's traffic through the proxy.
- **Compatible**: Works with popular Android emulators like **Mumu Player** and **Bluestacks**.

---

## How it Works

The process involves three main components:
1.  **An Android Emulator**: A virtual Android device running on your PC. We recommend **Mumu Player**.
2.  **EveryProxy App**: An Android app that starts HTTP & SOCKS proxy servers on the emulator.
3.  **emuVPN**: A script that runs on your PC to forward the emulator's proxy ports to `localhost`, making the connection accessible to Windows.

<img src="adbC.gif" alt="adbC">

---

## Setup Guide

### Step 1: Install Prerequisites

1.  **Install ADB:**
    - Download and install `adb-setup-1.4.3.exe` from the official release. This will install the Android Debug Bridge (ADB) system-wide on your PC.
    - [**Download adb-setup-1.4.3.zip**](https://github.com/Alireza-Ghavabesh/adb/releases/download/v1.9.0/adb-setup-1.4.3.zip)

2.  **Install an Android Emulator:**
    - You need an Android emulator to run the VPN app.
    - We **highly recommend Mumu Player** for the best performance and stability with this tool.
    - **Bluestacks** is also tested and works well.
    - After installing, make sure you **enable "USB Debugging"** in the emulator's developer settings.

### Step 2: Configure the Emulator

1.  **Install EveryProxy:**
    - In your emulator, install the **EveryProxy** Android app from the Google Play Store or an APK provider.

2.  **Configure EveryProxy Settings:**
    - Open EveryProxy.
    - Go to **Settings**.
    - Change **IP Address** to `0.0.0.0`.
    - Set the **HTTP Port** to `63254`.
    - Set the **SOCKS Port** to `63255`.

    <img src="step4.gif" alt="EveryProxy Settings" style="width:700px;height:400px;">

### Step 3: Set Up emuVPN

1.  **Download and Place `emuVPN.exe`:**
    - Download `emuVPN.zip` from the latest release.
    - [**Download emuVPN.zip**](https://github.com/Alireza-Ghavabesh/adb/releases/download/v1.9.5/emuVPN.zip)
    - Extract the zip file and copy `emuVPN.exe` to the Windows startup folder. This ensures it runs automatically every time you log in.
    - **Startup Path:** `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`

2.  **Restart Your PC:**
    - A restart is required to ensure ADB services and the startup application run correctly.

---

## Usage

### Step 1: Activate the Connection in Android

1.  Connect to your desired VPN inside the Android emulator.
2.  Open the **EveryProxy** app and enable the **HTTP proxy toggle**.

### Step 2: Configure Windows Proxy Settings

1.  On Windows, go to **Settings > Network & Internet > Proxy**.
2.  Under "Manual proxy setup", turn on **Use a proxy server**.
3.  Set the **Address** to `127.0.0.1`.
4.  Set the **Port** to `63254`.
5.  Click **Save**. Your browser and many other Windows apps will now use the emulator's VPN.

### Optional: Using SOCKS Proxy

- If you have an application that supports a SOCKS proxy (like Nekoray), you can use the following details:
  - **Address**: `127.0.0.1`
  - **Port**: `63255`

---

## ⚠ Important Note for Nekoray (TUN Mode)

If you plan to use Nekoray's TUN mode (a system-wide VPN mode), you must prevent it from routing ADB and the emulator's traffic through itself, which would create a connection loop.

- In the Nekoray app, go to **Preferences -> Tun settings**.
- In the **Bypass Process Name** window, add the following two lines:
  ```
  HD-Player.exe
  emuVPN.exe
  ```
- This will prevent a connection loop between Windows and the emulator.

# Enjoy!
