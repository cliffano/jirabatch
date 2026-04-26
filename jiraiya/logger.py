"""Logger for Jiraiya."""

from conflog import Conflog

_logger = None


def init():
    """Initialize logger.

    Returns a cached logger instance to prevent duplicate handlers
    from being added on repeated calls.
    """

    global _logger  # pylint: disable=global-statement
    if _logger is not None:
        return _logger

    cfl = Conflog(
        conf_dict={"level": "info", "format": "[jiraiya] %(levelname)s %(message)s"}
    )

    _logger = cfl.get_logger(__name__)
    return _logger
