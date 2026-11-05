import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { MessageStore } from '../src/storage/database.js';

const migrationsDirectory = path.resolve(import.meta.dirname, '..', 'migrations');

test('deduplikasi bertahan setelah database dibuka ulang', () => {
  const temporaryDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'akari-storage-'));
  const databaseFile = path.join(temporaryDirectory, 'data', 'akari.sqlite');

  try {
    const firstProcess = new MessageStore({ databaseFile, migrationsDirectory });
    assert.equal(firstProcess.claimIncoming('message-1'), true);
    firstProcess.markReplied('message-1');
    assert.equal(firstProcess.getStatus('message-1'), 'replied');
    firstProcess.close();

    const restartedProcess = new MessageStore({ databaseFile, migrationsDirectory });
    assert.equal(restartedProcess.claimIncoming('message-1'), false);
    assert.equal(restartedProcess.getStatus('message-1'), 'replied');
    restartedProcess.close();
  } finally {
    fs.rmSync(temporaryDirectory, { recursive: true, force: true });
  }
});
