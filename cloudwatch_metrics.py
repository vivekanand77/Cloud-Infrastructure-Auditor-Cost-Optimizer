from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import TypedDict, Optional
import boto3
logger = logging.getLogger(__name__)

class UnderutilizedInstance(TypedDict):
    instance_id       : str
    region            : str
    avg_cpu_percent   : float
    days_analyzed     : int
    threshold_percent : float
    flagged_at        : str   # ISO-8601 UTC, e.g. "2026-06-28T10:30:00+00:00"
    account_id        : str   # e.g. "123456789012"


def get_low_cpu_instances(
    threshold: float = 5.0,
    days: int = 14,
    region: str = "ap-south-1",
    boto_session: Optional[boto3.Session] = None,
) -> list[UnderutilizedInstance]:
    """
    
    -------
    >>> results = get_low_cpu_instances(threshold=5.0, days=14)
    >>> for r in results:
    ...     print(r["instance_id"], r["avg_cpu_percent"])
    """
    # ── Placeholder — logic goes here in Week 2 ───────────────────────────────
    logger.info(
        "get_low_cpu_instances() called | threshold=%.1f%% | days=%d | region=%s",
        threshold, days, region
    )
    return []   # ← replace with real implementation
if __name__ == "__main__":
    print("✅ cloudwatch_metrics.py imported cleanly")
    print(f"   Schema keys : {list(UnderutilizedInstance.__annotations__.keys())}")
    print(f"   Stub result : {get_low_cpu_instances()}")
    print("   Ready for Dhruv's aggregator ✓")