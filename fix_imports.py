import os

for root, dirs, files in os.walk('backend/tests'):
    for f in files:
        if f.endswith('.py') and f != 'conftest.py':
            path = os.path.join(root, f)
            with open(path, 'r') as fp:
                content = fp.read()
            if 'pytestmark = pytest.mark.postgres' in content and 'import pytest' not in content:
                lines = content.split('\n')
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''") and not line.startswith('import') and not line.startswith('from '):
                        insert_idx = i
                        break
                lines.insert(insert_idx, 'import pytest')
                with open(path, 'w') as fp:
                    fp.write('\n'.join(lines))
                print(f'Added import pytest to {path}')