"""Verify Hermes routing without printing secrets or sending another model request."""
import contextlib
import io
import os
import pathlib
import sys

home = pathlib.Path(r"C:\Users\Akari\AppData\Local\hermes")
os.environ["HERMES_HOME"] = str(home)
sys.path.insert(0, str(home / "hermes-agent"))
try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from dotenv import load_dotenv
        load_dotenv(home / ".env", override=True)
        from hermes_cli.config import load_config
        from hermes_cli.runtime_provider import resolve_runtime_provider
        cfg = load_config()
        model = cfg["model"]
        runtime = resolve_runtime_provider(requested=model["provider"], target_model=model["default"])
    checks = {
        "MODEL_IS_AKARI": model["default"] == "akari",
        "ENDPOINT_IS_9ROUTER": runtime["base_url"].rstrip("/") == "http://127.0.0.1:20128/v1",
        "DEDICATED_KEY_RESOLVED": runtime["api_key"] == os.environ["AKARI_9ROUTER_API_KEY"],
        "CHAT_COMPLETIONS": runtime["api_mode"] == "chat_completions",
    }
    for name, valid in checks.items():
        print(f"{name}={valid}")
    sys.exit(0 if all(checks.values()) else 1)
except Exception as exc:
    print("RUNTIME_VERIFICATION_FAILED=" + type(exc).__name__)
    sys.exit(1)
