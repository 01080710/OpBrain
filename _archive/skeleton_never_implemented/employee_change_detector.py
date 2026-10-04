"""
Detects employee / team / shift changes and data anomalies by comparing
cleaned data against a previous snapshot (e.g. yesterday vs today).
"""


def detect(clean_data):
    """
    Detect changes and anomalies from cleaned data.

    Args:
        clean_data: Cleaned data returned by processors.data_cleaner.clean().

    Returns:
        Detected changes/anomalies. Exact format to be defined when this
        is implemented.
    """
    raise NotImplementedError("employee_change_detector.detect() is not implemented yet.")
