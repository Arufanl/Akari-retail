import { GoogleGenAI } from '@google/genai';

export function createGeminiClient({ apiKey, model, systemInstruction, maxOutputTokens }) {
  const client = new GoogleGenAI({ apiKey });

  return Object.freeze({
    async replyTo(text) {
      const response = await client.models.generateContent({
        model,
        contents: text,
        config: {
          systemInstruction,
          maxOutputTokens,
        },
      });
      const reply = response.text?.trim();
      if (!reply) {
        throw new Error('Gemini mengembalikan balasan kosong.');
      }
      return reply;
    },
  });
}
