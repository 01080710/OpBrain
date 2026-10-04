"""
Cleans and standardizes raw data collected from PBI and Lark into a
single unified format that the rest of the pipeline can rely on.
"""


def clean(raw_pbi_data, raw_lark_data):
    """
    Clean and standardize raw data from multiple sources.

    Args:
        raw_pbi_data: Raw data returned by collectors.pbi_collector.fetch().
        raw_lark_data: Raw data returned by collectors.lark_collector.fetch().

    Returns:
        Cleaned, standardized data. Exact format (expected: pandas DataFrame)
        to be defined when this is implemented.
    """
    raise NotImplementedError("data_cleaner.clean() is not implemented yet.")
