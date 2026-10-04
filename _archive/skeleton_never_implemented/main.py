"""
Entry point / Orchestrator for the OP Workforce Intelligence & Automation System.

This module only coordinates the pipeline steps below, in order. Business
logic for each step must live in its own module under src/ — do not add
data processing, metrics, or report logic directly in this file.
"""

from src.collectors import pbi_collector, lark_collector
from src.processors import data_cleaner, employee_change_detector
from src.metrics import workforce_metrics
from src.reports import daily_report, lark_writer
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_daily_pipeline():
    logger.info("Daily pipeline started")

    # Step 1: Data Collection
    raw_pbi_data = pbi_collector.fetch()
    raw_lark_data = lark_collector.fetch()

    # Step 2: Data Cleaning / Standardization
    clean_data = data_cleaner.clean(raw_pbi_data, raw_lark_data)

    # Step 3: Change / Anomaly Detection
    changes = employee_change_detector.detect(clean_data)

    # Step 4: Metrics Calculation
    metrics = workforce_metrics.calculate(clean_data)

    # Step 5: AI Analysis
    # TODO: connect src/ai/analyzer.py once AI analysis is implemented.
    # AI analysis must only receive cleaned/structured data (metrics, changes),
    # never raw_pbi_data / raw_lark_data directly.
    # ai_result = analyzer.analyze(metrics, changes)

    # Step 6: Report Generation
    report = daily_report.generate(metrics, changes)

    # Step 7: Update Lark
    lark_writer.push(report)

    logger.info("Daily pipeline finished")


if __name__ == "__main__":
    run_daily_pipeline()
