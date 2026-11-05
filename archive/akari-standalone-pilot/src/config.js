import fs from 'node:fs';
import path from 'node:path';

const PLACEHOLDER = 'replace-';

function failConfiguration(message) {
  const error = new Error(message);
  error.name = 'ConfigurationError';
  throw error;
}

function requireNonEmpty(value, name) {
  if (typeof value !== 'string' || value.trim() === '') {
    failConfiguration(`${name} wajib diisi.`);
  }
  return value.trim();
}

function assertWritableDirectory(directory) {
  fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  fs.accessSync(directory, fs.constants.R_OK | fs.constants.W_OK);
}

export function loadConfig({ env = process.env } = {}) {
  const homeValue = requireNonEmpty(env.AKARI_HOME, 'AKARI_HOME');
  const home = path.resolve(homeValue);
  assertWritableDirectory(home);

  const secretsFile = path.join(home, 'secrets', '.env');
  if (fs.existsSync(secretsFile)) {
    process.loadEnvFile(secretsFile);
  }

  const runtimeConfigFile = path.join(home, 'config', 'akari.json');
  if (!fs.existsSync(runtimeConfigFile)) {
    failConfiguration(`Konfigurasi runtime belum ada di ${runtimeConfigFile}`);
  }

  let runtimeConfig;
  try {
    runtimeConfig = JSON.parse(fs.readFileSync(runtimeConfigFile, 'utf8'));
  } catch {
    failConfiguration('config/akari.json bukan JSON yang valid.');
  }
  const geminiModel = requireNonEmpty(runtimeConfig.geminiModel, 'geminiModel');
  if (geminiModel.startsWith(PLACEHOLDER)) {
    failConfiguration('geminiModel masih berupa placeholder.');
  }

  if (!Array.isArray(runtimeConfig.allowedWhatsAppJids) || runtimeConfig.allowedWhatsAppJids.length === 0) {
    failConfiguration('allowedWhatsAppJids wajib berisi minimal satu JID.');
  }
  const allowedWhatsAppJids = runtimeConfig.allowedWhatsAppJids.map((jid) =>
    requireNonEmpty(jid, 'allowedWhatsAppJids[]'),
  );
  if (allowedWhatsAppJids.some((jid) => jid.startsWith(PLACEHOLDER))) {
    failConfiguration('allowedWhatsAppJids masih berisi placeholder.');
  }

  const apiKey = requireNonEmpty(process.env.GEMINI_API_KEY, 'GEMINI_API_KEY');
  if (apiKey.startsWith(PLACEHOLDER)) {
    failConfiguration('GEMINI_API_KEY masih berupa placeholder.');
  }
  const pairingNumber = process.env.WHATSAPP_PAIRING_NUMBER?.replace(/\D/g, '') || null;
  if (pairingNumber && !/^\d{7,15}$/.test(pairingNumber)) {
    failConfiguration('WHATSAPP_PAIRING_NUMBER harus 7-15 digit tanpa tanda +.');
  }

  const replyMaxOutputTokens = runtimeConfig.replyMaxOutputTokens ?? 300;
  if (!Number.isInteger(replyMaxOutputTokens) || replyMaxOutputTokens < 1 || replyMaxOutputTokens > 2048) {
    failConfiguration('replyMaxOutputTokens harus bilangan bulat 1-2048.');
  }

  const projectRoot = path.resolve(import.meta.dirname, '..');
  return Object.freeze({
    home,
    apiKey,
    pairingNumber,
    geminiModel,
    replyMaxOutputTokens,
    allowedWhatsAppJids: Object.freeze(allowedWhatsAppJids),
    authDirectory: path.join(home, 'auth', 'baileys'),
    databaseFile: path.join(home, 'data', 'akari.sqlite'),
    promptFile: path.join(projectRoot, 'prompts', 'akari-system.txt'),
  });
}

export function ensureRuntimeDirectories(config) {
  for (const directory of [
    path.dirname(config.databaseFile),
    config.authDirectory,
    path.join(config.home, 'backups'),
    path.join(config.home, 'logs'),
  ]) {
    assertWritableDirectory(directory);
  }
}
