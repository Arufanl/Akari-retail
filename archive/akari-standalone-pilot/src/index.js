import fs from 'node:fs';
import path from 'node:path';
import pino from 'pino';
import { createMessageHandler } from './app/message-handler.js';
import { loadConfig, ensureRuntimeDirectories } from './config.js';
import { createGeminiClient } from './llm/gemini.js';
import { MessageStore } from './storage/database.js';
import { startWhatsApp } from './whatsapp/client.js';

const logger = pino({
  level: process.env.AKARI_LOG_LEVEL ?? 'info',
  base: undefined,
  redact: ['apiKey', 'pairingNumber', 'jid', 'text', 'message'],
});

let store;
let whatsapp;

try {
  const config = loadConfig();
  ensureRuntimeDirectories(config);
  const systemInstruction = fs.readFileSync(config.promptFile, 'utf8').trim();
  const migrationsDirectory = path.resolve(import.meta.dirname, '..', 'migrations');

  store = new MessageStore({ databaseFile: config.databaseFile, migrationsDirectory });
  const gemini = createGeminiClient({
    apiKey: config.apiKey,
    model: config.geminiModel,
    systemInstruction,
    maxOutputTokens: config.replyMaxOutputTokens,
  });

  whatsapp = await startWhatsApp({
    authDirectory: config.authDirectory,
    pairingNumber: config.pairingNumber,
    createOnMessage: (sendText) =>
      createMessageHandler({
        allowedJids: config.allowedWhatsAppJids,
        store,
        gemini,
        sendText,
        logger,
      }),
    logger,
  });
} catch (error) {
  logger.fatal(
    {
      event: 'startup_failed',
      errorName: error?.name ?? 'Error',
      reason: error?.name === 'ConfigurationError' ? error.message : undefined,
    },
    'Akari gagal dimulai.',
  );
  store?.close();
  process.exitCode = 1;
}

function shutdown(signal) {
  logger.info({ event: 'shutdown', signal }, 'Akari dihentikan dengan aman.');
  whatsapp?.stop();
  store?.close();
  process.exit(0);
}

process.once('SIGINT', () => shutdown('SIGINT'));
process.once('SIGTERM', () => shutdown('SIGTERM'));
