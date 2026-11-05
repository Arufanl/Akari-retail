from pathlib import Path
import re
root = Path(r'C:\Users\Akari\AppData\Local\hermes\logs')
for name in ['errors.log', 'gateway.log', 'gateway-exit-diag.log']:
    print('LOG=' + name)
    for line in (root / name).read_text(encoding='utf-8', errors='replace').splitlines()[-100:]:
        for pattern in [r'(?:ModuleNotFoundError|ImportError|AttributeError|TypeError|SyntaxError|RuntimeError|PermissionError|NameError|ValueError)\b', r'File "[^\"]+\.py", line \d+', r'(?:No module named|cannot import name) [\x27\x22][a-zA-Z0-9_.]+', r'(?i)already running|restart|fatal|shutdown|exit code']:
            match = re.search(pattern, line)
            if match:
                print(match.group(0))
