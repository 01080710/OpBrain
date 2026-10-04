"""
Generates the daily report from calculated metrics and detected changes.
Output should be written under output/daily/.
"""


def generate(metrics, changes):
    """
    Generate the daily report.

    Args:
        metrics: Calculated metrics returned by metrics.workforce_metrics.calculate().
        changes: Detected changes/anomalies returned by
            processors.employee_change_detector.detect().

    Returns:
        The generated report. Exact format to be defined when this is
        implemented.
    """
    raise NotImplementedError("daily_report.generate() is not implemented yet.")
