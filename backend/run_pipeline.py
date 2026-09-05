"""
Standalone CLI Runner for Resilient Weather Ingestion Pipeline.
Runs NMA scraper -> Quality Validation -> Open-Meteo Fallback -> TimescaleDB/PostgreSQL/SQLite.

Usage:
    python run_pipeline.py
"""
import sys
import os
import json
import logging

# Ensure backend root is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.pipeline.orchestrator import run_resilient_ingest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

if __name__ == "__main__":
    print("=" * 60)
    print("  Ethiopian Weather Dashboard - Resilient Ingestion Pipeline")
    print("=" * 60)
    metrics = run_resilient_ingest()
    print("\nExecution Summary:")
    print(json.dumps(metrics.model_dump(), indent=2))
    if metrics.success:
        print("\nPipeline execution succeeded!")
        sys.exit(0)
    else:
        print("\nPipeline execution encountered errors.")
        sys.exit(1)
