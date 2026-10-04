from __future__ import annotations

import pandas as pd


def derive_transaction_features(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    if {"amount", "previous_transaction_amount"}.issubset(working.columns):
        working["amount_deviation"] = working["amount"] - working["previous_transaction_amount"]

    if {"amount", "balance_before", "balance_after"}.issubset(working.columns):
        working["balance_change"] = working["balance_after"] - working["balance_before"]

    if {"amount", "transaction_frequency"}.issubset(working.columns):
        working["amount_to_frequency"] = working["amount"] / (working["transaction_frequency"].replace(0, 1))

    if "transaction_time" in working.columns:
        working["transaction_hour"] = pd.to_datetime(working["transaction_time"], errors="coerce").dt.hour

    if "transaction_date" in working.columns:
        working["transaction_day"] = pd.to_datetime(working["transaction_date"], errors="coerce").dt.day

    if "is_international" in working.columns:
        working["is_international"] = working["is_international"].astype(str).str.lower().isin(["true", "1", "yes"])

    if {"amount", "previous_transaction_amount"}.issubset(working.columns):
        working["relative_amount_ratio"] = working["amount"] / (working["previous_transaction_amount"].replace(0, 1))

    return working
