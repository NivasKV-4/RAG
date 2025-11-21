"""
File utility functions for FlightLens
"""

import os
import json
from pathlib import Path
from typing import Generator, Dict, Any

def ensure_dirs():
    """
    Create all required directories for FlightLens
    """
    directories = [
        "data/raw",
        "data/processed",
        "models/faiss_index",
        "evaluate/results",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def read_jsonl(path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Read JSONL file line by line
    
    Args:
        path: Path to JSONL file
    
    Yields:
        Parsed JSON objects
    """
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def write_jsonl(path: str, data: list):
    """
    Write list of dicts to JSONL file
    
    Args:
        path: Output file path
        data: List of dictionaries to write
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")

def count_jsonl_lines(path: str) -> int:
    """
    Count lines in JSONL file
    
    Args:
        path: Path to JSONL file
    
    Returns:
        Number of lines
    """
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


if __name__ == "__main__":
    print("Creating FlightLens directory structure...")
    ensure_dirs()
    print("\n✅ All directories created!")
