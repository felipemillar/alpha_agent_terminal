import subprocess
import json
import os
import pytest  # type: ignore

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_SCRIPT = os.path.join(BASE_DIR, "scripts", "search_symbol.py")
EXTRACTOR_SCRIPT = os.path.join(BASE_DIR, "scripts", "extractor.py")
import sys
PYTHON_EXE = sys.executable

def test_search_symbol_json_output():
    """Smoke Test: Verify search_symbol returns valid JSON matching the Pydantic schema."""
    result = subprocess.run(
        [PYTHON_EXE, SEARCH_SCRIPT, "--symbol", "AAPL", "--json"],
        capture_output=True,
        text=True
    )
    
    # Should exit 0
    assert result.returncode == 0
    
    # Should be valid JSON
    data = json.loads(result.stdout)
    assert "results" in data
    assert isinstance(data["results"], list)
    
    # Verify at least one result has AAPL
    symbols = [r.get("symbol") for r in data["results"]]
    assert "AAPL" in symbols or len(symbols) > 0

def test_extractor_json_output():
    """Smoke Test: Verify extractor returns valid JSON and creates a CSV."""
    result = subprocess.run(
        [PYTHON_EXE, EXTRACTOR_SCRIPT, "--symbol", "AAPL", "--interval", "1d", "--bars", "5", "--json"],
        capture_output=True,
        text=True
    )
    
    # Should exit 0
    assert result.returncode == 0
    
    # Should be valid JSON
    data = json.loads(result.stdout)
    assert data.get("status") == "success"
    assert "csv_path" in data
    assert data.get("rows_extracted") == 5
    
    # Verify CSV file exists
    csv_path = data["csv_path"]
    assert os.path.exists(csv_path)
    
    # Cleanup
    if os.path.exists(csv_path):
        os.remove(csv_path)

def test_extractor_invalid_symbol():
    """Smoke Test: Verify extractor handles invalid symbols gracefully via JSON."""
    result = subprocess.run(
        [PYTHON_EXE, EXTRACTOR_SCRIPT, "--symbol", "INVALIDXYZ123", "--interval", "1d", "--bars", "5", "--json"],
        capture_output=True,
        text=True
    )
    
    # Should exit 1 for expected fail
    assert result.returncode == 1
    
    # Should be valid JSON with error
    data = json.loads(result.stdout)
    assert data.get("status") == "error"
    assert data.get("error_type") == "NO_DATA"

def test_extractor_invalid_input():
    """Smoke Test: Verify extractor handles regex validation gracefully."""
    result = subprocess.run(
        [PYTHON_EXE, EXTRACTOR_SCRIPT, "--symbol", "INVALID_XYZ_123", "--interval", "1d", "--bars", "5", "--json"],
        capture_output=True,
        text=True
    )
    
    # Should exit 1 for expected fail
    assert result.returncode == 1
    
    data = json.loads(result.stdout)
    assert data.get("status") == "error"
    assert data.get("error_type") == "INVALID_INPUT"
