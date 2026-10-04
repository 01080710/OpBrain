"""
Calculates OP workforce metrics (Workload, Productivity, FRT, AHT,
Task Mix, Team/Individual/Shift Performance, etc.) from cleaned data.
"""


def calculate(clean_data):
    """
    Calculate workforce metrics from cleaned data.

    Args:
        clean_data: Cleaned data returned by processors.data_cleaner.clean().

    Returns:
        Calculated metrics. Exact format to be defined when this is
        implemented.
    """
    raise NotImplementedError("workforce_metrics.calculate() is not implemented yet.")
