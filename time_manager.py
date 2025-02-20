import ntptime
import time
from datetime import datetime, timezone
import config

class TimeManager:
    def __init__(self, logger):
        self.last_sync = 0
        self.last_sync_success = 0
        self.drift_history = []  # Store recent drift measurements
        self.current_server_index = 0
        self.logger = logger
        
    def _try_ntp_server(self, server):
        """Try to sync with a specific NTP server"""
        try:
            self.logger.debug(f"Attempting to sync with NTP server: {server}")
            ntptime.host = server
            ntptime.settime()
            self.logger.debug(f"Successfully synced with {server}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to sync with {server}: {str(e)}")
            return False
            
    def _calculate_drift(self):
        """Calculate time drift since last sync"""
        if not self.last_sync_success:
            self.logger.debug("No previous successful sync, skipping drift calculation")
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
                
            self.logger.debug(f"Calculated drift: {drift} seconds")
            return drift
            
        self.logger.warning("Failed to calculate drift - sync failed")
        return None
        
    def _get_average_drift_rate(self):
        """Calculate average drift rate in seconds per hour"""
        if not self.drift_history:
            self.logger.debug("No drift history available")
            return None
            
        total_drift = sum(self.drift_history)
        avg_drift = total_drift / len(self.drift_history)
        time_span = (time.time() - self.last_sync_success) / 3600  # Convert to hours
        
        if time_span > 0:
            drift_rate = avg_drift / time_span
            self.logger.debug(f"Average drift rate: {drift_rate} seconds/hour")
            return drift_rate
            
        self.logger.warning("Invalid time span for drift calculation")
        return None
        
    def sync_time(self):
        """Synchronize time with NTP server with retry logic"""
        self.logger.info("Starting time synchronization")
        
        # First try primary server
        if self._try_ntp_server(config.NTP_SERVER):
            self.last_sync = time.time()
            self.last_sync_success = self.last_sync
            self.logger.info("Time synchronized with primary NTP server")
            return True
            
        # If primary fails, try backup servers
        for server in config.NTP_BACKUP_SERVERS:
            self.logger.info(f"Trying backup NTP server: {server}")
            if self._try_ntp_server(server):
                self.last_sync = time.time()
                self.last_sync_success = self.last_sync
                self.logger.info(f"Time synchronized with backup NTP server: {server}")
                return True
                
            # Wait before trying next server
            time.sleep(1)
            
        self.logger.error("All NTP servers failed")
        return False
        
    def ensure_time_synced(self):
        """Ensure time is synced with NTP server with dynamic interval"""
        current_time = time.time()
        
        # Calculate time since last sync
        time_since_sync = current_time - self.last_sync
        
        # Check if it's time to sync
        if time_since_sync >= config.NTP_SYNC_INTERVAL:
            self.logger.debug("Sync interval reached, checking drift")
            
            # Calculate drift
            drift = self._calculate_drift()
            
            # If drift is significant (more than 1 second), sync immediately
            if drift and abs(drift) > 1:
                self.logger.warning(f"Significant drift detected: {drift} seconds")
                return self.sync_time()
                
            # Get average drift rate
            drift_rate = self._get_average_drift_rate()
            
            # If drift rate is high, decrease sync interval
            if drift_rate and abs(drift_rate) > 1:  # More than 1 second per hour
                self.logger.warning(f"High drift rate detected: {drift_rate} seconds/hour")
                # Temporarily reduce sync interval by half
                if time_since_sync >= (config.NTP_SYNC_INTERVAL / 2):
                    self.logger.info("Performing early sync due to high drift rate")
                    return self.sync_time()
            
            # Normal sync interval
            self.logger.info("Performing regular sync")
            return self.sync_time()
            
        self.logger.debug("Time sync not needed yet")
        return True
    
    def get_utc_timestamp(self):
        """Get current UTC timestamp"""
        return time.time()
    
    def format_utc_datetime(self, timestamp):
        """Format timestamp as UTC datetime string for Google Calendar API"""
        dt = datetime.fromtimestamp(timestamp, timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def parse_datetime(self, dt_str):
        """Parse datetime string from Google Calendar API to timestamp"""
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.replace(tzinfo=timezone.utc).timestamp() 