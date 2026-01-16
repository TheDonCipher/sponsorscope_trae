from enum import Enum

class DataCompleteness(str, Enum):
    """
    Represents the completeness of the data gathered during the scraping process.
    Used to signal graceful degradation in the analysis and reporting layers.
    """
    FULL = "full"
    PARTIAL_NO_COMMENTS = "partial_no_comments"
    PARTIAL_NO_IMAGES = "partial_no_images"
    TEXT_ONLY = "text_only"
    ARCHIVAL = "archival"  # Data from cache/history, no fresh scrape
    UNAVAILABLE = "unavailable" # Private or deleted
    FAILED = "failed"

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"

class ScrapeStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
