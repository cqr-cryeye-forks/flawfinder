import enum


@enum.unique
class SeverityLevel(enum.StrEnum):
    INFO = "info"
    # Represents non-critical information that may be useful for understanding the system
    #   but does not indicate a security or operational issue.

    LOW = "low"
    # Indicates a minor issue that has a low impact on the system and its operations.

    MEDIUM = "medium"
    # Represents an issue of moderate severity that may cause disruptions or inefficiencies.

    HIGH = "high"
    # Signifies a significant issue that can have a major impact on the system's functionality or security.

    CRITICAL = "critical"
    # Represents a critical issue that poses a severe threat to the system, data, or operations.
