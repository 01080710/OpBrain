"""
AI analysis module.

Must only receive already cleaned and structured data (metrics, changes) —
never raw data from collectors. This keeps AI analysis decoupled from
how data is collected or cleaned, so the AI approach can change without
affecting the rest of the pipeline.
"""


def analyze(metrics, changes):
    """
    Analyze cleaned, structured metrics and detected changes to explain
    what happened, where anomalies occurred, and who / which team / shift
    is affected.

    Args:
        metrics: Calculated metrics returned by metrics.workforce_metrics.calculate().
        changes: Detected changes/anomalies returned by
            processors.employee_change_detector.detect().

    Returns:
        AI analysis result. Exact format to be defined when this is
        implemented.
    """
    raise NotImplementedError("ai.analyzer.analyze() is not implemented yet.")
