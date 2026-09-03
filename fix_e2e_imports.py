import os

test_files = [
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
    
    if 'pytestmark = pytest.mark.postgres' in content and 'import pytest' not in content:
        lines = content.split('\n')
        # Insert import pytest at the top
        lines.insert(0, 'import pytest')
        with open(path, 'w') as fp:
            fp.write('\n'.join(lines))
        print(f'Fixed {path}')