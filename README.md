# MicroPython Busy Light

> **⚠️ WORK IN PROGRESS**: This project is currently under development and awaiting hardware for testing. The code is untested and may require adjustments once hardware testing begins.

A smart busy light system using a Seeed Studio XIAO RP2350 and WS2812B 8x8 LED Matrix that integrates with Google Calendar. The display shows your current availability and meeting time information:

- Red: In a meeting
- Green: Available
- Blue: Updating
- Orange: Error state

The rightmost column shows:
- When busy: Time remaining in current meeting (bottom-up, blue)
- When free: Time until next meeting (top-down, dimmed green)
- When meetings > 80 minutes: Full column in overflow color

## Hardware Requirements

- Seeed Studio XIAO RP2350
- WS2812B 8x8 LED Matrix Panel
- USB cable for power and programming
- Jumper wires

## Wiring Instructions

1. Connect the WS2812B LED Matrix to the XIAO RP2350:
   - Connect VDD (Power) to 3.3V or 5V on the XIAO
   - Connect GND (Ground) to GND on the XIAO
   - Connect DIN (Data In) to GPIO pin 16 (or your preferred GPIO pin)

## Software Setup

1. Install MicroPython on your XIAO RP2350:
   - Download the latest MicroPython firmware for RP2040 from [micropython.org](https://micropython.org)
   - Flash the firmware using the appropriate tools

2. Install required packages:
   ```bash
   mpremote mip install -r requirements.txt
   ```
   Or manually install each package:
   ```bash
   mpremote mip install micropython-jwt
   mpremote mip install micropython-base64
   mpremote mip install micropython-json
   mpremote mip install micropython-urequests
   ```

3. Clone this repository:
   ```bash
   git clone https://github.com/speedracer833/busylight.git
   cd busylight
   ```

4. Create your local configuration:
   ```bash
   cp config_template.py config_local.py
   ```
   Edit `config_local.py` with your:
   - WiFi credentials
   - Service account key (JSON)
   - Calendar IDs

## Google Calendar Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name it "busylight-service"
   - Click "Create and Continue"
   - Skip role assignment
   - Click "Done"

5. Create a Service Account Key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON"
   - Download the key file

6. Share Your Calendars:
   - Open the downloaded JSON file
   - Copy the "client_email" value
   - Go to Google Calendar
   - For each calendar you want to monitor:
     - Find the calendar in the left sidebar
     - Click the three dots > "Settings and sharing"
     - Under "Share with specific people"
     - Click "Add people"
     - Paste the service account email
     - Set permission to "See all event details"
     - Click "Send"
   - Copy each Calendar ID from "Integrate calendar" section

7. Update `config_local.py`:
   - Paste the entire contents of the service account JSON key file
   - Add all calendar IDs to the CALENDAR_IDS list

## Project Structure

- `main.py` - Main program logic
- `neopixel.py` - WS2812B LED control module
- `calendar_api.py` - Google Calendar integration
- `config.py` - Base configuration settings
- `config_template.py` - Template for local settings
- `config_local.py` - Your local settings (not in git)
- `time_manager.py` - NTP time synchronization

## Features

- Real-time calendar status display
- Multiple calendar support
- Meeting time remaining indicator
- Next meeting countdown
- Automatic time synchronization via NTP
- Multiple NTP server fallback
- Drift detection and compensation
- Back-to-back meeting detection

## Development

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Pre-commit Hook

This repository includes a pre-commit hook that checks for sensitive information in your commits. The hook will:
- Scan all staged files for potential sensitive data
- Check for API keys, tokens, passwords, and other sensitive information
- Prevent commits that might leak sensitive data
- Ignore template files and example configurations

To enable the pre-commit hook:
```bash
chmod +x .git/hooks/pre-commit
```

The hook checks for:
- Private keys and secrets
- API tokens and keys
- Passwords and credentials
- WiFi configurations
- Email addresses
- URLs and endpoints
- Other potentially sensitive data

If sensitive data is found, the commit will be blocked and you'll see:
- The file containing sensitive data
- The line number where it was found
- A description of the sensitive data
- The actual content that triggered the warning

To bypass the hook in special cases (use with caution):
```bash
git commit --no-verify
```

Note: The hook ignores:
- Files in `.git`, `venv`, `__pycache__`, and `node_modules`
- The `config_local.py` file (where your actual credentials should be stored)
- Template files with placeholder values
- Comments containing example data

## Troubleshooting

1. If the LED matrix doesn't light up:
   - Check your wiring connections
   - Verify the power supply is adequate
   - Ensure the data pin matches your configuration

2. If calendar events aren't updating:
   - Check your WiFi connection
   - Verify your service account key
   - Check that calendars are shared with the service account
   - Check the serial output for error messages

3. If time sync fails:
   - Check your internet connection
   - Try changing the NTP server in `config.py`
   - Verify your timezone settings

## License

This project is licensed under the MIT License - see the LICENSE file for details. 