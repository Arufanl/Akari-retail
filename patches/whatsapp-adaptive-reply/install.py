"""Install this local patch with backups; leave credentials and sessions untouched."""
from datetime import datetime, timezone
from pathlib import Path
import ast
import copy
import shutil
import sys
sys.path.insert(0, r'C:\Users\Akari\AppData\Local\hermes\hermes-agent')
import hermes_bootstrap
import hermes_yaml as yaml
from ruamel.yaml import YAML

home = Path(r'C:\Users\Akari\AppData\Local\hermes')
plugin = home / 'hermes-agent/plugins/platforms/whatsapp'
source = Path(__file__).resolve().parent
config_path = home / 'config.yaml'
config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
desired = copy.deepcopy(config)
wa = desired.setdefault('platforms', {}).setdefault('whatsapp', {})
wa.setdefault('extra', {})['reply_quote_mode'] = 'adaptive'
for name in ['adapter.py', 'reply_quotes.py']:
    ast.parse((source / name).read_text(encoding='utf-8'))
backup = home / 'backups' / ('pre-adaptive-reply-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(parents=True)
shutil.copy2(config_path, backup / 'config.yaml')
shutil.copy2(plugin / 'adapter.py', backup / 'adapter.py')
if (plugin / 'reply_quotes.py').exists():
    shutil.copy2(plugin / 'reply_quotes.py', backup / 'reply_quotes.py')
# Keep every unrelated YAML value identical. Reformat only the authored WhatsApp block.
text = config_path.read_text(encoding='utf-8')
tree = YAML(typ='safe').compose(text)
platforms = next((v for k, v in tree.value if k.value == 'platforms'), None)
existing = next(((k, v) for k, v in platforms.value if k.value == 'whatsapp'), None) if platforms else None
if existing:
    key, value = existing
    lines = text.splitlines(keepends=True)
    block = yaml.safe_dump({'whatsapp': wa}, sort_keys=False, allow_unicode=True, width=4096)
    block = ''.join(' ' * key.start_mark.column + line if line.strip() else line for line in block.splitlines(keepends=True))
    lines[key.start_mark.line:value.end_mark.line] = [block]
    updated = ''.join(lines)
else:
    updated = yaml.safe_dump(desired, sort_keys=False, allow_unicode=True, width=4096)
assert yaml.safe_load(updated) == desired, 'YAML preservation check failed'
shutil.copy2(source / 'reply_quotes.py', plugin / 'reply_quotes.py')
shutil.copy2(source / 'adapter.py', plugin / 'adapter.py')
config_path.write_text(updated, encoding='utf-8')
assert yaml.safe_load(config_path.read_text(encoding='utf-8')) == desired
print('BACKUP=' + str(backup))
print('ADAPTIVE_REPLY_INSTALLED=True')
print('UNRELATED_CONFIG_PRESERVED=True')
