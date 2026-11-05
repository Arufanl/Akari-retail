import makeWASocket, { DisconnectReason, useMultiFileAuthState } from 'baileys';
import pino from 'pino';

const RECONNECT_DELAY_MS = 3_000;

export async function startWhatsApp({ authDirectory, pairingNumber, createOnMessage, logger }) {
  const { state, saveCreds } = await useMultiFileAuthState(authDirectory);
  let socket;
  let stopped = false;

  const connect = async () => {
    const wasRegistered = state.creds.registered;
    socket = makeWASocket({
      auth: state,
      logger: pino({ level: 'silent' }),
      markOnlineOnConnect: false,
      syncFullHistory: false,
    });
    const onMessage = createOnMessage((jid, text) => socket.sendMessage(jid, { text }));

    socket.ev.on('creds.update', saveCreds);
    socket.ev.on('messages.upsert', async ({ type, messages }) => {
      if (type !== 'notify') return;
      for (const message of messages) {
        await onMessage(message);
      }
    });

    socket.ev.on('connection.update', ({ connection, lastDisconnect }) => {
      if (connection === 'open') {
        logger.info({ event: 'whatsapp_connected' }, 'WhatsApp terhubung.');
      }
      if (connection !== 'close' || stopped) return;

      const statusCode = lastDisconnect?.error?.output?.statusCode;
      if (statusCode === DisconnectReason.loggedOut) {
        logger.error({ event: 'whatsapp_logged_out' }, 'Sesi WhatsApp logout; pairing ulang diperlukan.');
        return;
      }
      logger.warn({ event: 'whatsapp_reconnecting' }, 'Koneksi terputus; mencoba menghubungkan kembali.');
      setTimeout(() => {
        void connect().catch((error) => {
          logger.error(
            { event: 'whatsapp_reconnect_failed', errorName: error?.name ?? 'Error' },
            'Percobaan menghubungkan ulang gagal.',
          );
        });
      }, RECONNECT_DELAY_MS);
    });

    if (!wasRegistered) {
      if (!pairingNumber) {
        logger.error(
          { event: 'pairing_number_missing' },
          'WHATSAPP_PAIRING_NUMBER wajib diisi untuk pairing pertama.',
        );
        throw new Error('WHATSAPP_PAIRING_NUMBER wajib diisi untuk pairing pertama.');
      }
      const code = await socket.requestPairingCode(pairingNumber);
      process.stdout.write(`Kode pairing WhatsApp (rahasia sementara): ${code}\n`);
    }
  };

  await connect();
  return Object.freeze({
    sendText(jid, text) {
      return socket.sendMessage(jid, { text });
    },
    stop() {
      stopped = true;
      void socket?.end(undefined);
    },
  });
}
