export function extractText(message) {
  return (
    message?.conversation ??
    message?.extendedTextMessage?.text ??
    message?.ephemeralMessage?.message?.conversation ??
    message?.ephemeralMessage?.message?.extendedTextMessage?.text ??
    null
  );
}

function normalizeJid(jid) {
  return jid.replace(/^([^:@]+):\d+@/, '$1@');
}

export function createMessageHandler({ allowedJids, store, gemini, sendText, logger }) {
  const allowlist = new Set(allowedJids.map(normalizeJid));

  return async function handleMessage(message) {
    const key = message?.key;
    if (!key?.id || key.fromMe) return 'ignored';

    const primaryJid = key.remoteJid;
    if (!primaryJid || primaryJid.endsWith('@g.us') || primaryJid.includes('@broadcast') || primaryJid.endsWith('@newsletter')) {
      return 'ignored';
    }

    const senderCandidates = [key.remoteJid, key.remoteJidAlt, key.participant, key.participantAlt].filter(Boolean);
    const senderJid = senderCandidates.find((jid) => allowlist.has(normalizeJid(jid)));
    if (!senderJid) return 'ignored';

    const text = extractText(message?.message)?.trim();
    if (!text) return 'ignored';

    try {
      if (!store.claimIncoming(key.id)) {
        logger.info({ event: 'duplicate_ignored' }, 'Pesan duplikat diabaikan.');
        return 'duplicate';
      }
      const reply = await gemini.replyTo(text);
      await sendText(primaryJid, reply);
      store.markReplied(key.id);
      logger.info({ event: 'reply_sent' }, 'Satu balasan terkirim.');
      return 'replied';
    } catch (error) {
      try {
        store.markFailed(key.id);
      } catch {
        // The original failure remains the useful signal; never log message contents.
      }
      logger.error(
        { event: 'reply_failed', errorName: error?.name ?? 'Error' },
        'Pemrosesan pesan gagal; isi pesan dan identitas tidak dicatat.',
      );
      return 'failed';
    }
  };
}
