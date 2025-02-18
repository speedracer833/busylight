import network
import time
from machine import Pin
import config
from neopixel import NeoPixel
from calendar_api import CalendarAPI
from time_manager import TimeManager

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi connected!')
    print('Network config:', wlan.ifconfig())

def main():
    # Initialize LED matrix
    led_matrix = NeoPixel(config.LED_PIN, config.LED_COUNT, config.LED_BRIGHTNESS)
    led_matrix.fill(config.COLOR_UPDATING)  # Blue while starting up
    
    # Progress indicator column (using rightmost column)
    PROGRESS_COLUMN = config.MATRIX_WIDTH - 1
    
    # Connect to WiFi
    try:
        connect_wifi()
    except Exception as e:
        print("WiFi connection failed:", e)
        led_matrix.fill(config.COLOR_ERROR)
        return
    
    # Initialize time manager and sync time
    time_manager = TimeManager()
    if not time_manager.sync_time():
        print("Initial time sync failed")
        led_matrix.fill(config.COLOR_ERROR)
        return
    
    # Initialize Calendar API with time manager
    calendar = CalendarAPI(time_manager)
    
    while True:
        try:
            # Show updating status
            led_matrix.fill(config.COLOR_UPDATING)
            
            # Check calendar status
            is_busy, remaining_minutes, next_meeting_in = calendar.get_calendar_status()
            
            if is_busy is None:
                # Error occurred
                led_matrix.fill(config.COLOR_ERROR)
            else:
                # Update main display (all columns except progress column)
                main_color = config.COLOR_BUSY if is_busy else config.COLOR_FREE
                led_matrix.fill_except_column(main_color, PROGRESS_COLUMN)
                
                # Update progress column based on status
                if is_busy and remaining_minutes > 0:
                    # Show remaining time in current meeting
                    led_matrix.set_progress_column(PROGRESS_COLUMN, remaining_minutes)
                elif not is_busy and next_meeting_in is not None:
                    # Show countdown to next meeting
                    led_matrix.set_next_meeting_column(PROGRESS_COLUMN, next_meeting_in)
                else:
                    # No current or upcoming meetings
                    for y in range(config.MATRIX_HEIGHT):
                        led_matrix.set_pixel_xy(PROGRESS_COLUMN, y, config.COLOR_OFF)
                
                # Show the updates
                led_matrix.show()
                
                # Print status to console
                if is_busy:
                    print(f"In a meeting. {remaining_minutes} minutes remaining")
                elif next_meeting_in is not None:
                    print(f"Next meeting in {next_meeting_in} minutes")
                else:
                    print("No upcoming meetings")
                
        except Exception as e:
            print("Error in main loop:", e)
            led_matrix.fill(config.COLOR_ERROR)
            
        # Wait before next update
        time.sleep(config.UPDATE_INTERVAL)

if __name__ == '__main__':
    main() 