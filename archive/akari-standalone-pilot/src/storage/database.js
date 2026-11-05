import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

export class MessageStore {
  #database;

  constructor({ databaseFile, migrationsDirectory }) {
    fs.mkdirSync(path.dirname(databaseFile), { recursive: true, mode: 0o700 });
    this.#database = new DatabaseSync(databaseFile);
    this.#database.exec('PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;');
    this.#migrate(migrationsDirectory);
  }

  #migrate(migrationsDirectory) {
    const migration = fs.readFileSync(path.join(migrationsDirectory, '001_initial.sql'), 'utf8');
    this.#database.exec(migration);
    this.#database
      .prepare('INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)')
      .run(1, new Date().toISOString());
  }

  claimIncoming(whatsappMessageId, receivedAt = new Date()) {
    const result = this.#database
      .prepare(`
        INSERT OR IGNORE INTO processed_messages
          (whatsapp_message_id, status, received_at)
        VALUES (?, 'processing', ?)
      `)
      .run(whatsappMessageId, receivedAt.toISOString());
    return Number(result.changes) === 1;
  }

  markReplied(whatsappMessageId, repliedAt = new Date()) {
    this.#database
      .prepare(`
        UPDATE processed_messages
        SET status = 'replied', replied_at = ?, error_code = NULL
        WHERE whatsapp_message_id = ?
      `)
      .run(repliedAt.toISOString(), whatsappMessageId);
  }

  markFailed(whatsappMessageId, errorCode = 'processing_failed') {
    this.#database
      .prepare(`
        UPDATE processed_messages
        SET status = 'failed', error_code = ?
        WHERE whatsapp_message_id = ?
      `)
      .run(errorCode, whatsappMessageId);
  }

  getStatus(whatsappMessageId) {
    return this.#database
      .prepare('SELECT status FROM processed_messages WHERE whatsapp_message_id = ?')
      .get(whatsappMessageId)?.status;
  }

  close() {
    this.#database.close();
  }
}
