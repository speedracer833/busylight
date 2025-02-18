import ntptime
import time
import config
import machine

class TimeManager:
    def __init__(self):
        self.last_sync = 0
        self.last_sync_success = 0
        self.drift_history = []  # Store recent drift measurements
        self.current_server_index = 0
        
    def _try_ntp_server(self, server):
        """Try to sync with a specific NTP server"""
        try:
            ntptime.host = server
            ntptime.settime()
            return True
        except:
            return False
            
    def _calculate_drift(self):
        """Calculate time drift since last sync"""
        if not self.last_sync_success:
            return None
            
        # Get current time before sync
        pre_sync_time = time.time()
        
        # Try to sync
        if self._try_ntp_server(config.NTP_SERVER):
            # Get time after sync
            post_sync_time = time.time()
            
            # Calculate drift (in seconds)
            drift = post_sync_time - pre_sync_time
            
            # Store drift history (keep last 5 measurements)
            self.drift_history.append(drift)
            if len(self.drift_history) > 5:
                self.drift_history.pop(0)
                
            return drift
        return None
        
    def _get_average_drift_rate(self):
        """Calculate average drift rate in seconds per hour"""
        if not self.drift_history:
            return None
            
        total_drift = sum(self.drift_history)
        avg_drift = total_drift / len(self.drift_history)
        time_span = (time.time() - self.last_sync_success) / 3600  # Convert to hours
        
        if time_span > 0:
            return avg_drift / time_span
        return None
        
    def sync_time(self):
        """Synchronize time with NTP server with retry logic"""
        # First try primary server
        if self._try_ntp_server(config.NTP_SERVER):
            self.last_sync = time.time()
            self.last_sync_success = self.last_sync
            print("Time synchronized with primary NTP server")
            return True
            
        # If primary fails, try backup servers
        for server in config.NTP_BACKUP_SERVERS:
            print(f"Trying backup NTP server: {server}")
            if self._try_ntp_server(server):
                self.last_sync = time.time()
                self.last_sync_success = self.last_sync
                print(f"Time synchronized with backup NTP server: {server}")
                return True
                
            # Wait before trying next server
            time.sleep(1)
            
        print("All NTP servers failed")
        return False
        
    def ensure_time_synced(self):
        """Ensure time is synced with NTP server with dynamic interval"""
        current_time = time.time()
        
        # Calculate time since last sync
        time_since_sync = current_time - self.last_sync
        
        # Check if it's time to sync
        if time_since_sync >= config.NTP_SYNC_INTERVAL:
            # Calculate drift
            drift = self._calculate_drift()
            
            # If drift is significant (more than 1 second), sync immediately
            if drift and abs(drift) > 1:
                print(f"Significant drift detected: {drift} seconds")
                return self.sync_time()
                
            # Get average drift rate
            drift_rate = self._get_average_drift_rate()
            
            # If drift rate is high, decrease sync interval
            if drift_rate and abs(drift_rate) > 1:  # More than 1 second per hour
                print(f"High drift rate detected: {drift_rate} seconds/hour")
                # Temporarily reduce sync interval by half
                if time_since_sync >= (config.NTP_SYNC_INTERVAL / 2):
                    return self.sync_time()
            
            # Normal sync interval
            return self.sync_time()
            
        return True
    
    def get_utc_timestamp(self):
        """Get current UTC timestamp"""
        return time.time()
    
    def format_utc_datetime(self, timestamp):
        """Format timestamp as UTC datetime string for Google Calendar API"""
        tm = time.gmtime(timestamp)
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
            tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
        )
    
    def parse_datetime(self, dt_str):
        """Parse datetime string from Google Calendar API to timestamp"""
        # Format: "2024-03-20T15:30:00Z"
        year = int(dt_str[0:4])
        month = int(dt_str[5:7])
        day = int(dt_str[8:10])
        hour = int(dt_str[11:13])
        minute = int(dt_str[14:16])
        second = int(dt_str[17:19])
        
        # Convert to tuple for mktime (year, month, day, hour, minute, second, weekday, yearday)
        dt_tuple = (year, month, day, hour, minute, second, 0, 0)
        return time.mktime(dt_tuple) 