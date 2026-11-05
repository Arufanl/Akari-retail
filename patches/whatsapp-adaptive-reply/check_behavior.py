"""Offline transport checks; no WhatsApp connection or model request."""
import asyncio
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parent
os.environ['HERMES_HOME'] = tempfile.mkdtemp(prefix='akari-quote-check-')
sys.path.insert(0, r'C:\Users\Akari\AppData\Local\hermes\hermes-agent')


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


Policy = load('plugins.platforms.whatsapp.reply_quotes', 'reply_quotes.py').AdaptiveReplyQuotes
module = load('plugins.platforms.whatsapp.adaptive_check', 'adapter.py')
from gateway.platforms.base import SendResult


class QuoteChecks(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.chat = '12345@s.whatsapp.net'
        self.policy = Policy()
        self.adapter = object.__new__(module.WhatsAppAdapter)
        self.adapter._adaptive_reply_quotes = self.policy
        self.adapter.format_message = lambda text: text
        self.adapter.truncate_message = lambda text, limit: [text]
        self.adapter._outgoing_chunk_limit = lambda: 4000
        self.adapter._bridge_unavailable = AsyncMock(return_value=None)
        self.adapter._post_bridge_message = AsyncMock(return_value=SendResult(success=True, message_id='out'))

    async def send(self, anchor='one', **kwargs):
        return await self.adapter.send(self.chat, 'answer', reply_to=anchor, **kwargs)

    async def test_single_plain_and_next_single_plain(self):
        for mid in ['one', 'two']:
            self.policy.note(self.chat, mid)
            self.assertTrue((await self.send(mid)).success)
            self.assertNotIn('replyTo', self.adapter._post_bridge_message.call_args.args[1])

    async def test_burst_quotes_target_and_preserves_newer(self):
        self.policy.note(self.chat, 'one')
        self.policy.note(self.chat, 'two')
        await self.send()
        self.assertEqual(self.adapter._post_bridge_message.call_args.args[1]['replyTo'], 'one')
        self.assertIsNone(self.policy.anchor(self.chat, 'two'))

    async def test_batch_answer_clears_both(self):
        self.policy.note(self.chat, 'one')
        self.policy.note(self.chat, 'two')
        await self.send('two')
        self.assertEqual(self.adapter._post_bridge_message.call_args.args[1]['replyTo'], 'two')
        self.assertNotIn(self.chat, self.policy.pending)

    async def test_failed_send_keeps_pending(self):
        self.policy.note(self.chat, 'one')
        self.adapter._post_bridge_message.return_value = SendResult(success=False, error='offline')
        self.assertFalse((await self.send()).success)
        self.assertEqual(self.policy.pending[self.chat], ['one'])

    async def test_new_arrival_during_send_is_retained(self):
        self.policy.note(self.chat, 'one')
        async def post(*args, **kwargs):
            self.policy.note(self.chat, 'two')
            return SendResult(success=True, message_id='out')
        self.adapter._post_bridge_message.side_effect = post
        await self.send()
        self.assertEqual(self.policy.pending[self.chat], ['two'])

    async def test_interim_send_does_not_consume_pending(self):
        self.policy.note(self.chat, 'one')
        await self.send(metadata={'_interim_send': True})
        self.assertEqual(self.policy.pending[self.chat], ['one'])

    async def test_groups_and_unknown_targets_keep_quotes(self):
        self.policy.note(self.chat, 'one', is_group=True)
        await self.send()
        self.assertEqual(self.adapter._post_bridge_message.call_args.args[1]['replyTo'], 'one')

    async def test_other_chat_does_not_trigger_quote(self):
        self.policy.note(self.chat, 'one')
        self.policy.note('other', 'two')
        await self.send()
        self.assertNotIn('replyTo', self.adapter._post_bridge_message.call_args.args[1])


if __name__ == '__main__':
    unittest.main(verbosity=1)
