# MicroPython Busy Light

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

2. Clone this repository:
   ```bash
   git clone https://github.com/speedracer833/busylight.git
   cd busylight
   ```

3. Create your local configuration:
   ```bash
   cp config_template.py config_local.py
   ```
   Edit `config_local.py` with your:
   - WiFi credentials
   - Google Calendar API credentials
   - Calendar ID

## Google Calendar Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials
5. Get your refresh token (see below)
6. Add the credentials to your `config_local.py`

### Getting a Refresh Token

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download the client configuration
3. Use the Google OAuth 2.0 Playground to:
   - Configure your OAuth credentials
   - Authorize the Calendar API
   - Exchange authorization code for tokens
4. Copy the refresh token to your `config_local.py`

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

## Troubleshooting

1. If the LED matrix doesn't light up:
   - Check your wiring connections
   - Verify the power supply is adequate
   - Ensure the data pin matches your configuration

2. If calendar events aren't updating:
   - Check your WiFi connection
   - Verify your Google Calendar API credentials
   - Check the serial output for error messages

3. If time sync fails:
   - Check your internet connection
   - Try changing the NTP server in `config.py`
   - Verify your timezone settings

## License

This project is licensed under the MIT License - see the LICENSE file for details. 