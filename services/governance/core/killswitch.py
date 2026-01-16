import os

class KillSwitch:
    """
    Emergency control for system-wide operations.
    Reads from environment variables (fastest for Lambda/Container) or Redis.
    """
    
    @staticmethod
    def is_scan_enabled() -> bool:
        """
        If True, new scans are allowed.
        If False, system rejects new scan requests (HTTP 503).
        """
        # Default to True unless explicitly disabled
        return os.getenv("KILL_SWITCH_SCANS", "enabled").lower() == "enabled"

    @staticmethod
    def is_read_enabled() -> bool:
        """
        If True, cached reports are readable.
        If False, entire system is down (Maintenance Mode).
        """
        return os.getenv("KILL_SWITCH_READ", "enabled").lower() == "enabled"

    @staticmethod
    def get_maintenance_message() -> str:
        return os.getenv("MAINTENANCE_MESSAGE", "SponsorScope is currently undergoing scheduled maintenance.")
