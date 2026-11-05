# Patch Replay WhatsApp Hermes Tablet (Termux)

Patch ini dibuat untuk instalasi Hermes Agent di tablet Termux, commit `fd267bb3` (3 November 2026).

## Masalah yang Diatasi
1. Event Baileys `append` yang berisi riwayat percakapan lama tidak boleh diproses ulang oleh bot (mencegah pesan berulang saat koneksi terputus/tersambung kembali).
2. Pesan masuk (`inbound`) yang sudah pernah diproses disimpan sidik jarinya (SHA-256 fingerprint) di file persisten `processed-inbound-ids.jsonl` di dalam folder sesi.
3. Dedup bertahan melintasi restart proses bridge, dengan mekanisme pruning dan auto-compaction (maksimal 4096 entri).

## Berkas yang Ditambahkan / Dimodifikasi
- `scripts/whatsapp-bridge/inbound_message_gate.js` (berkas baru)
- `scripts/whatsapp-bridge/inbound_message_gate.test.mjs` (unit test baru, 6 test lolos)
- `scripts/whatsapp-bridge/bridge.js` (diintegrasikan)

## Cadangan Asli di Tablet
Cadangan `bridge.js` asli sebelum modifikasi tersimpan di:
`~/Hermes-Agent/scripts/whatsapp-bridge/bridge.js.bak-pre-dedup-20261105`

## Verifikasi Test
Di folder `~/Hermes-Agent/scripts/whatsapp-bridge`:
```bash
node --check bridge.js
node --check inbound_message_gate.js
node --test *.test.mjs
```
Hasil: **32 passed, 0 failed**.
