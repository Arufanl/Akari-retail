import assert from 'node:assert/strict';
import test from 'node:test';
import { createMessageHandler } from '../src/app/message-handler.js';

function makeHarness() {
  const claimed = new Set();
  const replies = [];
  let modelCalls = 0;
  const statuses = new Map();

  const handler = createMessageHandler({
    allowedJids: ['628111111111@s.whatsapp.net'],
    store: {
      claimIncoming(id) {
        if (claimed.has(id)) return false;
        claimed.add(id);
        return true;
      },
      markReplied(id) {
        statuses.set(id, 'replied');
      },
      markFailed(id) {
        statuses.set(id, 'failed');
      },
    },
    gemini: {
      async replyTo(text) {
        modelCalls += 1;
        return `Balasan untuk: ${text}`;
      },
    },
    async sendText(jid, text) {
      replies.push({ jid, text });
    },
    logger: { info() {}, error() {} },
  });

  return { handler, replies, statuses, getModelCalls: () => modelCalls };
}

test('satu pesan yang diizinkan menghasilkan satu balasan', async () => {
  const harness = makeHarness();
  const message = {
    key: { id: 'message-1', remoteJid: '628111111111@s.whatsapp.net', fromMe: false },
    message: { conversation: 'Halo' },
  };

  assert.equal(await harness.handler(message), 'replied');
  assert.equal(harness.getModelCalls(), 1);
  assert.deepEqual(harness.replies, [
    { jid: '628111111111@s.whatsapp.net', text: 'Balasan untuk: Halo' },
  ]);
  assert.equal(harness.statuses.get('message-1'), 'replied');
});

test('event duplikat tidak memanggil model atau mengirim balasan kedua', async () => {
  const harness = makeHarness();
  const message = {
    key: { id: 'message-1', remoteJid: '628111111111@s.whatsapp.net', fromMe: false },
    message: { conversation: 'Halo' },
  };

  assert.equal(await harness.handler(message), 'replied');
  assert.equal(await harness.handler(message), 'duplicate');
  assert.equal(harness.getModelCalls(), 1);
  assert.equal(harness.replies.length, 1);
});

test('nomor lain dan grup diabaikan sebelum model', async () => {
  const harness = makeHarness();
  const otherNumber = {
    key: { id: 'message-2', remoteJid: '628222222222@s.whatsapp.net', fromMe: false },
    message: { conversation: 'Rahasia' },
  };
  const group = {
    key: {
      id: 'message-3',
      remoteJid: '123456@g.us',
      participant: '628111111111@s.whatsapp.net',
      fromMe: false,
    },
    message: { conversation: 'Halo grup' },
  };

  assert.equal(await harness.handler(otherNumber), 'ignored');
  assert.equal(await harness.handler(group), 'ignored');
  assert.equal(harness.getModelCalls(), 0);
  assert.equal(harness.replies.length, 0);
});

test('remoteJidAlt dapat mencocokkan allowlist tanpa membalas grup', async () => {
  const harness = makeHarness();
  const message = {
    key: {
      id: 'message-4',
      remoteJid: '999999999999@lid',
      remoteJidAlt: '628111111111@s.whatsapp.net',
      fromMe: false,
    },
    message: { extendedTextMessage: { text: 'Halo dari LID' } },
  };

  assert.equal(await harness.handler(message), 'replied');
  assert.equal(harness.getModelCalls(), 1);
  assert.equal(harness.replies[0].jid, '999999999999@lid');
});

test('device suffix pada JID dinormalisasi untuk pemeriksaan allowlist', async () => {
  const harness = makeHarness();
  const message = {
    key: {
      id: 'message-5',
      remoteJid: '628111111111:12@s.whatsapp.net',
      fromMe: false,
    },
    message: { conversation: 'Halo dari perangkat tertaut' },
  };

  assert.equal(await harness.handler(message), 'replied');
  assert.equal(harness.getModelCalls(), 1);
});
