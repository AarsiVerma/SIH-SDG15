import os

# Fix all test files by moving import pytest to the top
test_files = [
    'backend/tests/unit/test_correlation.py',
    'backend/tests/unit/test_error_handler.py',
    'backend/tests/unit/test_event_engine.py',
    'backend/tests/unit/test_file_source.py',
    'backend/tests/unit/test_health.py',
    'backend/tests/unit/test_incident_manager.py',
    'backend/tests/unit/test_risk_engine.py',
    'backend/tests/unit/test_worker.py',
]

for path in test_files:
    with open(path, 'r') as fp:
        content = fp.read()
    
    # Find pytestmark line and move import pytest before it
    lines = content.split('\n')
    new_lines = []
    found_pytestmark = False
    found_import_pytest = False
    
    for line in lines:
        if line.strip().startswith('import pytest'):
            found_import_pytest = True
            continue  # Skip, we'll add it at the top
        if 'pytestmark = pytest.mark.postgres' in line:
            if not found_import_pytest:
                new_lines.insert(0, 'import pytest')
            found_pytestmark = True
        new_lines.append(line)
    
    if not found_import_pytest and found_pytestmark:
        # Insert at the very beginning
        new_lines.insert(0, 'import pytest')
    
    with open(path, 'w') as fp:
        fp.write('\n'.join(new_lines))
    print(f'Fixed {path}')