from pathlib import Path
from jev_local_experiments.race import run_terminal_race

def test_run_terminal_race(capsys):
    suite_path = Path("benchmarks/diverse_300.jsonl")
    assert suite_path.exists()

    result = run_terminal_race(
        suite_path=suite_path,
        num_cases=10,
        demo_speedup=100.0,  # Fast execution for test runner
    )
    assert result == 0

    captured = capsys.readouterr()
    assert "RACE RESULTS" in captured.out
    assert "Speedup" in captured.out
