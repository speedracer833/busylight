import network
import time
from machine import Pin
import config
from neopixel import NeoPixel
from calendar_api import CalendarAPI
from time_manager import TimeManager
from log_config import setup_logging

def connect_wifi():
    """Connect to WiFi network"""
    logger = loggers['main']
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        logger.info('Connecting to WiFi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    logger.info('WiFi connected!')
    logger.debug(f'Network config: {wlan.ifconfig()}')

def main():
    # Set up logging
    global loggers
    loggers = setup_logging()
    logger = loggers['main']
    
    logger.info("Starting Busy Light")
    
    # Initialize LED matrix
    led_matrix = NeoPixel(config.LED_PIN, config.LED_COUNT, config.LED_BRIGHTNESS)
    led_matrix.fill(config.COLOR_UPDATING)  # Blue while starting up
    logger.info("LED matrix initialized")
    
    # Progress indicator column (using rightmost column)
    PROGRESS_COLUMN = config.MATRIX_WIDTH - 1
    
    # Connect to WiFi
    try:
        connect_wifi()
    except Exception as e:
        logger.error(f"WiFi connection failed: {str(e)}")
        led_matrix.fill(config.COLOR_ERROR)
        return
    
    # Initialize time manager and sync time
    time_manager = TimeManager(loggers['time'])
    if not time_manager.sync_time():
        logger.error("Initial time sync failed")
        led_matrix.fill(config.COLOR_ERROR)
        return
    
    # Initialize Calendar API with time manager
    calendar = CalendarAPI(time_manager, loggers['calendar'])
    
    logger.info("System initialized, entering main loop")
    
    while True:
        try:
            # Show updating status
            led_matrix.fill(config.COLOR_UPDATING)
            logger.debug("Checking calendar status")
            
            # Check calendar status
            is_busy, remaining_minutes, next_meeting_in = calendar.get_calendar_status()
            
            if is_busy is None:
                # Error occurred
                logger.error("Failed to get calendar status")
                led_matrix.fill(config.COLOR_ERROR)
            else:
                # Update main display (all columns except progress column)
                main_color = config.COLOR_BUSY if is_busy else config.COLOR_FREE
                led_matrix.fill_except_column(main_color, PROGRESS_COLUMN)
                
                # Update progress column based on status
                if is_busy and remaining_minutes > 0:
                    # Show remaining time in current meeting
                    led_matrix.set_progress_column(PROGRESS_COLUMN, remaining_minutes)
                    logger.info(f"Busy: {remaining_minutes} minutes remaining")
                elif not is_busy and next_meeting_in is not None:
                    # Show countdown to next meeting
                    led_matrix.set_next_meeting_column(PROGRESS_COLUMN, next_meeting_in)
                    logger.info(f"Available: Next meeting in {next_meeting_in} minutes")
                else:
                    # No current or upcoming meetings
                    for y in range(config.MATRIX_HEIGHT):
                        led_matrix.set_pixel_xy(PROGRESS_COLUMN, y, config.COLOR_OFF)
                    logger.info("Available: No upcoming meetings")
                
                # Show the updates
                led_matrix.show()
                
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            led_matrix.fill(config.COLOR_ERROR)
            
        # Wait before next update
        logger.debug(f"Waiting {config.UPDATE_INTERVAL} seconds before next update")
        time.sleep(config.UPDATE_INTERVAL)

if __name__ == '__main__':
    main() 