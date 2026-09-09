import pytest
import os
import subprocess

def test_graph_rebuild_idempotency():
    """
    Test that verifies the full graph rebuild script can be run idempotently.
    """
    script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "rebuild_graph.py")
    if not os.path.exists(script_path):
        pytest.skip(f"Script not found at {script_path}")
        
    # Run once
    result1 = subprocess.run(["python3", script_path], capture_output=True, text=True)
    assert result1.returncode == 0, f"Graph rebuild failed: {result1.stderr}"
    
    # Run twice
    result2 = subprocess.run(["python3", script_path], capture_output=True, text=True)
    assert result2.returncode == 0, f"Second graph rebuild failed: {result2.stderr}"
    
    # Success means the constraints didn't fail and no duplicate nodes caused crashes.
