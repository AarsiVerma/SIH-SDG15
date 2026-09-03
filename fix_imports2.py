import os

files = [
    'backend/tests/unit/test_bytetrack_tracker.py',
    'backend/tests/unit/test_correlation.py',
    'backend/tests/unit/test_error_handler.py',
    'backend/tests/unit/test_event_engine.py',
    'backend/tests/unit/test_file_source.py',
    'backend/tests/unit/test_health.py',
    'backend/tests/unit/test_incident_manager.py',
    'backend/tests/unit/test_risk_engine.py',
    'backend/tests/unit/test_worker.py',
]

for path in files:
    with open(path, 'r') as fp:
        content = fp.read()
    if 'import pytest' not in content:
        lines = content.split('\n')
        lines.insert(0, 'import pytest')
        with open(path, 'w') as fp:
            fp.write('\n'.join(lines))
        print(f'Added import pytest to {path}')