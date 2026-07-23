"""Verify all imports resolve correctly"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("Sprint 2.1 Import Verification")
print("=" * 50)

# Test imports
imports_to_test = [
    ("main", "main"),
    ("app.config.settings", "settings"),
    ("app.core.constants", "MissionStatus"),
    ("app.core.lifespan", "lifespan"),
    ("app.database.base", "Base"),
    ("app.database.connection", "engine"),
    ("app.security.jwt", "create_access_token"),
    ("app.security.auth", "hash_password"),
    ("app.security.dependencies", "DBSession"),
    ("app.middleware.cors", "setup_cors"),
    ("app.middleware.logging", "setup_logging"),
    ("app.utils.logger", "logger"),
    ("app.utils.exceptions", "ChildDNAException"),
    ("app.routers.system.health", "router"),
    ("app.api.v1.router", "api_router"),
]

all_ok = True
for module, attr in imports_to_test:
    try:
        mod = __import__(module, fromlist=[attr])
        getattr(mod, attr)
        print(f"[OK] {module}.{attr}")
    except Exception as e:
        print(f"[FAIL] {module}.{attr}: {e}")
        all_ok = False

print("=" * 50)
if all_ok:
    print("All imports resolved successfully!")
else:
    print("Some imports failed!")