# Import sensitive configuration from local config
try:
    from config_local import *
except ImportError:
    print("Please create config_local.py from config_template.py with your settings")
    raise

# Hardware Configuration
LED_PIN = 16  # GPIO pin connected to WS2812B data line
LED_COUNT = 64  # 8x8 matrix = 64 LEDs
LED_BRIGHTNESS = 0.3  # Brightness level (0.0 to 1.0)
MATRIX_WIDTH = 8
MATRIX_HEIGHT = 8

# Time Configuration
UPDATE_INTERVAL = 60  # How often to check calendar (in seconds)
NTP_SERVER = "pool.ntp.org"  # NTP server for time synchronization
NTP_SYNC_INTERVAL = 900  # How often to sync time (in seconds) - reduced to 15 minutes
NTP_RETRY_INTERVAL = 60  # How long to wait between retry attempts (in seconds)
NTP_MAX_RETRIES = 3  # Maximum number of retry attempts for NTP sync
NTP_BACKUP_SERVERS = [  # Backup NTP servers if primary fails
    "time.google.com",
    "time.cloudflare.com",
    "time.apple.com"
]
MINUTES_PER_LED = 10  # Each LED in progress column represents this many minutes

# Colors (RGB format)
COLOR_BUSY = (255, 0, 0)      # Red for main display
COLOR_FREE = (0, 255, 0)      # Green for main display
COLOR_UPDATING = (0, 0, 255)  # Blue while updating
COLOR_ERROR = (255, 165, 0)   # Orange for errors
COLOR_PROGRESS = (0, 191, 255)  # Deep Sky Blue for time remaining indicator
COLOR_OVERFLOW = (75, 0, 130)   # Indigo for overflow time indicator
COLOR_OFF = (0, 0, 0)        # Off state 