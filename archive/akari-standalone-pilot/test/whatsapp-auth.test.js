import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { useMultiFileAuthState } from 'baileys';

test('auth state Baileys dapat dibuka kembali setelah restart proses', async () => {
  const temporaryDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'akari-auth-'));

  try {
    const firstProcess = await useMultiFileAuthState(temporaryDirectory);
    firstProcess.state.creds.registered = true;
    firstProcess.state.creds.me = { id: '100000000000@s.whatsapp.net', name: 'test-only' };
    await firstProcess.saveCreds();

    const restartedProcess = await useMultiFileAuthState(temporaryDirectory);
    assert.equal(restartedProcess.state.creds.registered, true);
    assert.equal(restartedProcess.state.creds.me.id, '100000000000@s.whatsapp.net');
  } finally {
    fs.rmSync(temporaryDirectory, { recursive: true, force: true });
  }
});
