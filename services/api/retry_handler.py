import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class RetryHandler:
    """
    Handles retry logic with exponential backoff and jitter.
    Provides configurable retry behavior for async operations.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic and exponential backoff.
        
        Args:
            func: The async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the successful function execution
            
        Raises:
            Exception: The last exception if all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.config.max_retries + 1} for {func.__name__}")
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt == self.config.max_retries:
                    logger.error(f"Function {func.__name__} failed after {self.config.max_retries + 1} attempts")
                    break
                
                # Calculate delay with exponential backoff
                delay = self._calculate_delay(attempt)
                
                logger.warning(
                    f"Function {func.__name__} failed on attempt {attempt + 1}, "
                    f"retrying in {delay:.2f}s. Error: {str(e)}"
                )
                
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise last_exception or Exception("All retry attempts failed")
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay with exponential backoff and optional jitter.
        
        Args:
            attempt: The current attempt number (0-based)
            
        Returns:
            The calculated delay in seconds
        """
        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        
        # Cap at maximum delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            # Add random jitter (±25% of the delay)
            jitter_range = delay * 0.25
            delay = delay + random.uniform(-jitter_range, jitter_range)
            
            # Ensure delay is still positive
            delay = max(0.1, delay)
        
        return delay
    
    async def execute_with_conditional_retry(
        self,
        func: Callable,
        should_retry: Callable[[Exception], bool],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with conditional retry logic.
        
        Args:
            func: The async function to execute
            should_retry: Function that takes an exception and returns True if retry should occur
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the successful function execution
            
        Raises:
            Exception: The last exception if all retries are exhausted or should_retry returns False
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Conditional attempt {attempt + 1}/{self.config.max_retries + 1} for {func.__name__}")
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Function {func.__name__} succeeded on conditional attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry this specific exception
                if not should_retry(e):
                    logger.info(f"Function {func.__name__} failed with non-retryable error: {str(e)}")
                    raise
                
                if attempt == self.config.max_retries:
                    logger.error(f"Function {func.__name__} failed after {self.config.max_retries + 1} conditional attempts")
                    break
                
                # Calculate delay with exponential backoff
                delay = self._calculate_delay(attempt)
                
                logger.warning(
                    f"Function {func.__name__} failed on conditional attempt {attempt + 1}, "
                    f"retrying in {delay:.2f}s. Error: {str(e)}"
                )
                
                await asyncio.sleep(delay)
        
        # All retries exhausted
        raise last_exception or Exception("All conditional retry attempts failed")

# Default retry handler instance
default_retry_handler = RetryHandler()

# Specific retry configurations for different scenarios
SCRAPING_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    base_delay=2.0,
    max_delay=30.0,
    exponential_base=1.5
)

ANALYSIS_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0
)

ASSEMBLY_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    base_delay=0.5,
    max_delay=5.0,
    exponential_base=2.0
)

def is_network_error(exception: Exception) -> bool:
    """
    Check if an exception is network-related and should be retried.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if the exception is network-related and should be retried
    """
    error_str = str(exception).lower()
    network_errors = [
        "connection", "timeout", "network", "unavailable", "refused",
        "reset", "broken pipe", "dns", "host", " unreachable"
    ]
    
    return any(error in error_str for error in network_errors)

def is_rate_limit_error(exception: Exception) -> bool:
    """
    Check if an exception is rate limit related and should be retried with longer delay.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if the exception is rate limit related
    """
    error_str = str(exception).lower()
    rate_limit_errors = ["rate limit", "too many requests", "429", "quota"]
    
    return any(error in error_str for error in rate_limit_errors)