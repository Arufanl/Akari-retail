import os
from pathlib import Path
import sys
home = Path(r'C:\Users\Akari\AppData\Local\hermes')
os.environ['HERMES_HOME'] = str(home)
sys.path.insert(0, str(home / 'hermes-agent'))
import hermes_bootstrap
from gateway.config import load_gateway_config, Platform
from plugins.platforms.whatsapp.adapter import WhatsAppAdapter
config = load_gateway_config()
wa = config.platforms[Platform.WHATSAPP]
assert wa.extra['reply_quote_mode'] == 'adaptive'
adapter = WhatsAppAdapter(wa)
assert adapter._adaptive_reply_quotes is not None
print('GATEWAY_CONFIG_ADAPTIVE=True')
print('LIVE_ADAPTER_IMPORT_OK=True')
