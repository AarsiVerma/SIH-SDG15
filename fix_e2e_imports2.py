import os

test_files = [
    'backend/tests/e2e_scenarios/test_demo1_suspicious.py',
    'backend/tests/e2e_scenarios/test_demo2_wildlife.py',
    'backend/tests/e2e_scenarios/test_demo3_fire.py',
    'backend/tests/e2e_scenarios/test_demo4_camera.py',
    'backend/tests/e2e_scenarios/test_demo5_sos.py',
    'backend/tests/e2e_scenarios/test_demo6_correlation.py',
    'backend/tests/e2e_scenarios/test_demo7_offline.py',
    'backend/tests/integration/test_full_pipeline.py',
    'backend/tests/integration/test_cameras_api.py',
]

for path in test_files:
    with open(path, 'r') as fp:
        content = fp.read()
    
    lines = content.split('\n')
    new_lines = []
    found_import_pytest = False
    
    for line in lines:
        if line.strip().startswith('import pytest'):
            found_import_pytest = True
            continue
        if 'pytestmark = pytest.mark.postgres' in line:
            if not found_import_pytest:
                new_lines.insert(0, 'import pytest')
            found_import_pytest = True
        new_lines.append(line)
    
    if not found_import_pytest and 'pytestmark = pytest.mark.postgres' in content:
        new_lines.insert(0, 'import pytest')
    
    with open(path, 'w') as fp:
        fp.write('\n'.join(new_lines))
    print(f'Fixed {path}')