import json
import os
import sys
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from gwm_workflow.backends import AnalyticMockBackend
from gwm_workflow.config import load_config
from gwm_workflow.workflow import evaluate_candidate


def test_mock_run_writes_auditable_artifacts():
    path = os.path.join(os.path.dirname(__file__), "..", "configs", "beam_deflector_1550nm.json")
    settings = load_config(path)
    with tempfile.TemporaryDirectory() as directory:
        result = evaluate_candidate({}, settings, AnalyticMockBackend(), directory)
        assert result["attrs"]["valid_result"]
        assert result["metrics"]["forward_radiates"]
        for name in ["candidate.json", "phase_targets.csv", "scored_result.json"]:
            assert os.path.exists(os.path.join(directory, name))
        with open(os.path.join(directory, "candidate.json"), "r", encoding="utf-8") as handle:
            candidate = json.load(handle)
        assert candidate["config"]["metadata"]["doi"] == "10.1126/sciadv.abb4142"


if __name__ == "__main__":
    test_mock_run_writes_auditable_artifacts()
    print("mock workflow tests passed")
