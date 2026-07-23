"""Verification script for Sprint 2.1"""
import ast
import os

def verify_syntax(filepath):
    """Verify Python file has no syntax errors"""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, "OK"
    except SyntaxError as e:
        return False, str(e)

# Check all Python files
python_files = [
    'main.py',
    'app/config/settings.py',
    'app/core/constants.py',
    'app/core/lifespan.py',
    'app/database/base.py',
    'app/database/connection.py',
    'app/security/jwt.py',
    'app/security/auth.py',
    'app/security/dependencies.py',
    'app/middleware/cors.py',
    'app/middleware/logging.py',
    'app/utils/logger.py',
    'app/utils/exceptions.py',
    'app/routers/system/health.py',
    'app/api/v1/router.py',
    'tests/conftest.py',
    'tests/test_health.py',
]

print("Sprint 2.1 Verification")
print("=" * 50)

all_ok = True
for filepath in python_files:
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    if os.path.exists(full_path):
        ok, msg = verify_syntax(full_path)
        status = "[OK]" if ok else "[FAIL]"
        print(f"{status} {filepath}: {msg}")
        if not ok:
            all_ok = False
    else:
        print(f"[FAIL] {filepath}: File not found")
        all_ok = False

print("=" * 50)
if all_ok:
    print("All files have valid syntax!")
else:
    print("Some files have issues!")
