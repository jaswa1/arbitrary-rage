"""
Logging configuration for the application.
"""

import logging
import sys
from typing import Dict, Any
import structlog
from app.core.config import settings


def configure_logging():
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )


# Configure logging on import
configure_logging()

# Create logger instance
logger = structlog.get_logger()


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""
    
    @property
    def logger(self):
        """Get a logger instance with class context."""
        return structlog.get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> Dict[str, Any]:
    """Log function call with parameters."""
    log_data = {
        "event": "function_call",
        "function": func_name,
        **kwargs
    }
    logger.info("Function called", **log_data)
    return log_data


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context information."""
    log_data = {
        "event": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        log_data.update(context)
    
    logger.error("Error occurred", **log_data, exc_info=True)