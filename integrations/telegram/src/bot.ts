import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load .env from same directory as this script
try {
  const envPath = resolve(dirname(fileURLToPath(import.meta.url)), '..', '.env');
  const envContent = readFileSync(envPath, 'utf-8');
  for (const line of envContent.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx > 0) {
      const key = trimmed.slice(0, eqIdx).trim();
      const val = trimmed.slice(eqIdx + 1).trim();
      if (!process.env[key]) process.env[key] = val;
    }
  }
} catch {}

import axios from 'axios';
import { callTelegramApi, formatUser } from './utils';
import { extractMedia, downloadTelegramFile, extractUrls, getStorageStats } from './media';
import { chat, clearSession, generatePromo } from './chat';
import {
  checkAccess,
  recordReview,
  markPaid,
  getUserStats,
  extractTextFromFile,
  analyzeLegalDocument,
} from './legal_review';
import { execSync } from 'child_process';

// ── Core4 Topic IDs (set in .env) ────────────────────────────────────────────
const TOPIC_JARVIS   = process.env.TELEGRAM_TOPIC_JARVIS   ? Number(process.env.TELEGRAM_TOPIC_JARVIS)   : undefined;
const TOPIC_HERMES   = process.env.TELEGRAM_TOPIC_HERMES   ? Number(process.env.TELEGRAM_TOPIC_HERMES)   : undefined;
const TOPIC_OPENCLAW = process.env.TELEGRAM_TOPIC_OPENCLAW ? Number(process.env.TELEGRAM_TOPIC_OPENCLAW) : undefined;
const TOPIC_HARVEY   = process.env.TELEGRAM_TOPIC_HARVEY   ? Number(process.env.TELEGRAM_TOPIC_HARVEY)   : undefined;

// ── Core4 Agent URLs ──────────────────────────────────────────────────────────
const JARVIS_URL   = process.env.JARVIS_URL   || 'http://127.0.0.1:18791';
const HERMES_URL   = process.env.HERMES_URL   || 'http://127.0.0.1:18790';

// ── Legacy config ─────────────────────────────────────────────────────────────
const ADMIN_ID = process.env.TELEGRAM_ADMIN_ID ? Number(process.env.TELEGRAM_ADMIN_ID) : undefined;
const TARGET_CHANNEL = process.env.TELEGRAM_TARGET_CHANNEL || '';

const pendingPromos = new Map<string, { chatId: number; promo: string; url?: string }>();

// ── Agent type ────────────────────────────────────────────────────────────────
type AgentName = 'jarvis' | 'hermes' | 'openclaw' | 'harvey';

/**
 * Resolve which agent should handle a message based on Telegram forum thread ID
 * and BOT_PERSONA env var (legacy single-persona mode).
 */
function resolveAgent(threadId?: number): AgentName | null {
  // Legacy single-persona overrides topic routing
  const persona = process.env.BOT_PERSONA as AgentName | undefined;
  if (persona === 'harvey' || persona === 'jarvis' || persona === 'openclaw' || persona === 'hermes') {
    return persona;
  }

  // Forum topic-based routing
  if (threadId !== undefined) {
    if (TOPIC_JARVIS   !== undefined && threadId === TOPIC_JARVIS)   return 'jarvis';
    if (TOPIC_HERMES   !== undefined && threadId === TOPIC_HERMES)   return 'hermes';
    if (TOPIC_OPENCLAW !== undefined && threadId === TOPIC_OPENCLAW) return 'openclaw';
    if (TOPIC_HARVEY   !== undefined && threadId === TOPIC_HARVEY)   return 'harvey';
  }

  return null; // unrecognised topic → legacy M0Claw default
}

// ── HTTP Bridges to Core4 Agents ──────────────────────────────────────────────

async function callJarvisAPI(userId: number, text: string): Promise<string> {
  try {
    const res = await axios.post(
      `${JARVIS_URL}/chat`,
      { text, user_id: String(userId) },
      { timeout: 60_000 },
    );
    const body = res.data as any;
    return body.reply ?? JSON.stringify(body);
  } catch (err: any) {
    const detail = err.response?.data?.detail ?? err.message;
    return `[Jarvis nicht erreichbar: ${detail}]`;
  }
}

async function callOpenClawBus(userId: number, text: string): Promise<string> {
  const intent = detectOpenClawIntent(text);
  try {
    const res = await axios.post(
      `${HERMES_URL}/dispatch`,
      {
        from: 'telegram',
        to: 'openclaw',
        type: 'task',
        intent,
        payload: { text, user_id: String(userId) },
      },
      { timeout: 60_000 },
    );
    const payload = (res.data as any)?.payload ?? {};
    return payload.reply ?? payload.stub ?? JSON.stringify(payload);
  } catch (err: any) {
    const detail = err.response?.data?.detail ?? err.message;
    return `[OpenClaw nicht erreichbar: ${detail}]`;
  }
}

async function callHermesStatus(): Promise<string> {
  try {
    const [agentsRes, goalsRes] = await Promise.allSettled([
      axios.get(`${HERMES_URL}/agents`, { timeout: 5_000 }).then(r => r.data),
      axios.get(`${HERMES_URL}/goals?status=in_progress`, { timeout: 5_000 }).then(r => r.data),
    ]);

    const agents: any[] = agentsRes.status === 'fulfilled' ? (agentsRes.value?.agents ?? []) : [];
    const goals: any[] = goalsRes.status === 'fulfilled' ? (goalsRes.value?.goals ?? []) : [];

    const agentLines = agents.map((a: any) => {
      const healthy = a.status === 'healthy';
      const icon = healthy ? '✅' : '⚠️';
      const name = (a.name as string).padEnd(10);
      const state = a.status ?? (healthy ? 'healthy' : 'degraded');
      return `  ${icon} ${name} ${state}`;
    });

    const lines = [
      '📡 Hermes Status (auto):',
      ...(agentLines.length ? agentLines : ['  (no agents registered)']),
      `Goals in_progress: ${goals.length}`,
    ];
    return lines.join('\n');
  } catch (err: any) {
    return `[Hermes nicht erreichbar: ${err.message}]`;
  }
}

function detectOpenClawIntent(text: string): string {
  const t = text.toLowerCase();
  if (/youtube|video|publish/i.test(t))     return 'youtube_publish';
  if (/tweet|x-post|xpost|social/i.test(t)) return 'content_creation';
  if (/code|script|implementier/i.test(t))  return 'code_generation';
  if (/browser|scrape|search/i.test(t))     return 'browser_action';
  return 'content_creation'; // default
}

// ── Helpers ───────────────────────────────────────────────────────────────────

async function sendTyping(botToken: string, chatId: number) {
  try {
    await callTelegramApi(botToken, 'sendChatAction', { chat_id: chatId, action: 'typing' });
  } catch (_) {}
}

async function sendReply(
  botToken: string,
  chatId: number,
  threadId: number | undefined,
  text: string,
  parseMode?: string,
) {
  const params: Record<string, any> = { chat_id: chatId, text };
  if (threadId !== undefined) params.message_thread_id = threadId;
  if (parseMode) params.parse_mode = parseMode;

  await callTelegramApi(botToken, 'sendMessage', params).catch(async () => {
    // Retry without parse_mode if markdown parse fails
    if (parseMode) {
      const plain: Record<string, any> = { chat_id: chatId, text };
      if (threadId !== undefined) plain.message_thread_id = threadId;
      await callTelegramApi(botToken, 'sendMessage', plain).catch(() => {});
    }
  });
}

// ── Main message handler ──────────────────────────────────────────────────────

async function handleMessage(botToken: string, message: any) {
  const chatId    = message.chat.id;
  const threadId  = message.message_thread_id as number | undefined;
  const text      = (message.text ?? message.caption ?? '').trim();
  const from      = message.from ? formatUser(message.from) : 'Unknown';
  const userId    = message.from?.id as number | undefined;

  console.log(`[${new Date().toISOString()}] ${from} [topic:${threadId ?? 'main'}]: ${text || '[media]'}`);

  const agent = resolveAgent(threadId);

  // ── Topic 2: Hermes — auto-only, silent except /status ───────────────────
  if (agent === 'hermes') {
    if (text === '/status' || text === '/hermes') {
      const status = await callHermesStatus();
      await sendReply(botToken, chatId, threadId, status);
    }
    // All other user messages are silently ignored in Hermes topic
    return;
  }

  // ── Commands ──────────────────────────────────────────────────────────────
  if (text.startsWith('/')) {
    const handled = await handleCommand(botToken, chatId, text, userId, threadId, agent);
    if (handled) return;
  }

  // ── Media handling ────────────────────────────────────────────────────────
  const media = extractMedia(message);
  if (media) {
    await sendTyping(botToken, chatId);
    try {
      const localPath = await downloadTelegramFile(botToken, media.fileId, media.fileName, media.type);
      const sizeKB = media.fileSize ? (media.fileSize / 1024).toFixed(1) : '?';

      // Harvey / harvey-topic: documents → Legal Review
      if ((agent === 'harvey') && media.type === 'document') {
        await handleLegalReview(botToken, chatId, userId, localPath, media.fileName, media.mimeType, threadId);
        return;
      }

      await sendReply(
        botToken, chatId, threadId,
        `${mediaEmoji(media.type)} Gespeichert: ${media.fileName} (${sizeKB} KB)\n${localPath}`,
      );
    } catch (err: any) {
      await sendReply(botToken, chatId, threadId, `Fehler beim Download: ${err.message}`);
    }

    const urls = extractUrls(message);
    if (urls.length > 0 && agent !== 'harvey') {
      await handlePromoFlow(botToken, chatId, urls, text, threadId);
    }
    return;
  }

  // ── Topic 1: Jarvis — bridge to :18791/chat ───────────────────────────────
  if (agent === 'jarvis') {
    if (!text) {
      await sendReply(botToken, chatId, threadId, 'Kein Text empfangen.');
      return;
    }
    await sendTyping(botToken, chatId);
    const reply = await callJarvisAPI(userId ?? chatId, text);
    for (const chunk of splitMessage(reply, 4000)) {
      await sendReply(botToken, chatId, threadId, chunk, 'Markdown');
    }
    return;
  }

  // ── Topic 3: OpenClaw — bridge via Hermes bus ─────────────────────────────
  if (agent === 'openclaw') {
    if (!text) {
      await sendReply(botToken, chatId, threadId, 'Kein Task-Text empfangen.');
      return;
    }
    await sendTyping(botToken, chatId);
    const reply = await callOpenClawBus(userId ?? chatId, text);
    for (const chunk of splitMessage(reply, 4000)) {
      await sendReply(botToken, chatId, threadId, chunk);
    }
    return;
  }

  // ── Topic 4 / harvey persona: Harvey legal + sales ────────────────────────
  const isHarveyAgent = agent === 'harvey';

  // URL handling → Promo Flow (not for Harvey)
  const urls = extractUrls(message);
  if (urls.length > 0 && !isHarveyAgent) {
    await sendTyping(botToken, chatId);
    await handlePromoFlow(botToken, chatId, urls, text, threadId);
    return;
  }

  // Forwarded / Long text → Promo Flow (not for Harvey)
  if (!isHarveyAgent) {
    if (message.forward_from || message.forward_from_chat) {
      if (text.length > 20) {
        await sendTyping(botToken, chatId);
        await handlePromoFlow(botToken, chatId, [], text, threadId);
        return;
      }
    }
    if (text.length > 100 && !text.endsWith('?')) {
      await sendTyping(botToken, chatId);
      await handlePromoFlow(botToken, chatId, [], text, threadId);
      return;
    }
  }

  // Contact
  if (message.contact) {
    const c = message.contact;
    await sendReply(
      botToken, chatId, threadId,
      `Kontakt: ${c.first_name} ${c.last_name ?? ''} ${c.phone_number ? `| Tel: ${c.phone_number}` : ''}`.trim(),
    );
    return;
  }

  // Location
  if (message.location) {
    await sendReply(
      botToken, chatId, threadId,
      `Standort: ${message.location.latitude}, ${message.location.longitude}`,
    );
    return;
  }

  // Default AI chat (legacy M0Claw + Harvey text)
  if (text) {
    await sendTyping(botToken, chatId);
    const reply = await chat(chatId, text);
    for (const chunk of splitMessage(reply, 4000)) {
      await sendReply(botToken, chatId, threadId, chunk, 'Markdown');
    }
    return;
  }

  await sendReply(botToken, chatId, threadId, 'Nachricht empfangen.');
}

// ── Command handler ───────────────────────────────────────────────────────────

async function handleCommand(
  botToken: string,
  chatId: number,
  text: string,
  userId?: number,
  threadId?: number,
  agent?: AgentName | null,
): Promise<boolean> {
  const cmd  = text.split(' ')[0].toLowerCase();
  const args = text.slice(cmd.length).trim();
  const isHarvey = agent === 'harvey';

  switch (cmd) {
    case '/start': {
      const greeting = agentGreeting(agent);
      await sendReply(botToken, chatId, threadId, greeting);
      return true;
    }

    case '/clear':
      clearSession(chatId);
      await sendReply(botToken, chatId, threadId, 'Chat-Verlauf geloescht.');
      return true;

    case '/status': {
      const uptime = process.uptime();
      const h = Math.floor(uptime / 3600);
      const m = Math.floor((uptime % 3600) / 60);
      const stats = getStorageStats();
      const model = process.env.AI_MODEL || 'unbekannt';
      const provider = process.env.OLLAMA_BASE_URL
        ? `Ollama (${process.env.OLLAMA_BASE_URL})`
        : process.env.ANTHROPIC_API_KEY
          ? 'Anthropic'
          : process.env.OPENAI_API_KEY
            ? `OpenAI-compatible (${process.env.AI_API_BASE || 'openai'})`
            : 'kein Provider';

      await sendReply(botToken, chatId, threadId, [
        `${agentLabel(agent)} Status`,
        `Uptime: ${h}h ${m}m`,
        `Model: ${model}`,
        `Provider: ${provider}`,
        `Dateien: ${stats.totalFiles} (${stats.totalSizeMB} MB)`,
      ].join('\n'));
      return true;
    }

    case '/hermes': {
      const status = await callHermesStatus();
      await sendReply(botToken, chatId, threadId, status);
      return true;
    }

    case '/ping':
      await sendReply(botToken, chatId, threadId, 'Pong!');
      return true;

    case '/models': {
      try {
        const out = execSync('ollama list 2>/dev/null', { timeout: 10000 }).toString().trim();
        const lines = out.split('\n').slice(0, 15);
        await sendReply(botToken, chatId, threadId, `Ollama Models:\n\n${lines.join('\n')}`);
      } catch {
        await sendReply(botToken, chatId, threadId, 'Ollama nicht erreichbar.');
      }
      return true;
    }

    case '/exec': {
      if (ADMIN_ID && userId !== ADMIN_ID) {
        await sendReply(botToken, chatId, threadId, 'Nicht autorisiert.');
        return true;
      }
      if (!args) {
        await sendReply(botToken, chatId, threadId, 'Usage: /exec <command>');
        return true;
      }
      try {
        const out = execSync(args, { timeout: 30000, maxBuffer: 1024 * 1024 }).toString().trim();
        const result = out.substring(0, 3500) || '(keine Ausgabe)';
        await sendReply(botToken, chatId, threadId, `$ ${args}\n\n${result}`);
      } catch (err: any) {
        const errMsg = (err.stderr?.toString() || err.message || 'Fehler').substring(0, 2000);
        await sendReply(botToken, chatId, threadId, `Fehler:\n${errMsg}`);
      }
      return true;
    }

    case '/system': {
      try {
        const hostname = execSync('hostname').toString().trim();
        const diskRaw  = execSync("df -h / | tail -1 | awk '{print $4}'").toString().trim();
        const ollamaRunning = execSync("pgrep -x ollama >/dev/null 2>&1 && echo 'running' || echo 'stopped'").toString().trim();
        await sendReply(botToken, chatId, threadId, [
          `System: ${hostname}`,
          `Disk frei: ${diskRaw}`,
          `Ollama: ${ollamaRunning}`,
        ].join('\n'));
      } catch (err: any) {
        await sendReply(botToken, chatId, threadId, `System-Info Fehler: ${err.message}`);
      }
      return true;
    }

    case '/credits': {
      if (isHarvey && userId) {
        const stats = getUserStats(userId);
        await sendReply(botToken, chatId, threadId, stats);
      } else {
        await sendReply(botToken, chatId, threadId, 'Nur für Harvey verfügbar.');
      }
      return true;
    }

    case '/subscribe': {
      if (!isHarvey) return false;
      const link    = process.env.STRIPE_PAYMENT_LINK ?? '';
      const monthly = process.env.LEGAL_MONTHLY_PRICE ?? '49€';
      const perDoc  = process.env.LEGAL_PER_DOC_PRICE ?? '9€';
      const lines = [
        'Harvey Premium freischalten:',
        '',
        `• ${perDoc} / Dokument (Einmalig)`,
        `• ${monthly} / Monat (Unbegrenzt)`,
        '',
        'Was du bekommst:',
        '• Unbegrenzte Dokument-Analysen',
        '• Vollständige Risikoanalyse',
        '• Klausel-Empfehlungen',
        '• Priority-Antwortzeit',
        '',
      ];
      if (link) {
        lines.push(`Jetzt upgraden:\n${link}`, '', 'Nach Zahlung: /paid eingeben.');
      } else {
        lines.push('Schreib "Premium anfragen" und wir melden uns.');
      }
      await sendReply(botToken, chatId, threadId, lines.join('\n'));
      return true;
    }

    case '/paid': {
      if (!isHarvey || !userId) return false;
      markPaid(userId);
      await sendReply(botToken, chatId, threadId, [
        'Harvey Premium aktiviert!',
        '',
        'Du hast jetzt unbegrenzte Dokument-Analysen.',
        'Schick einfach ein PDF, DOCX oder TXT.',
        '',
        '/credits - Status anzeigen',
      ].join('\n'));
      return true;
    }

    case '/review': {
      if (!isHarvey) return false;
      await sendReply(botToken, chatId, threadId, [
        'Dokument zur Analyse einschicken:',
        '',
        'Unterstützte Formate:',
        '• PDF (empfohlen)',
        '• DOCX / Word',
        '• TXT',
        '',
        'Einfach die Datei hier anhängen.',
        '',
        '/credits - Verbleibende Analysen',
        '/subscribe - Premium freischalten',
      ].join('\n'));
      return true;
    }

    case '/help': {
      await sendReply(botToken, chatId, threadId, agentHelp(agent));
      return true;
    }

    default:
      return false; // pass to AI / agent bridge
  }
}

// ── Agent greeting / help strings ────────────────────────────────────────────

function agentLabel(agent?: AgentName | null): string {
  switch (agent) {
    case 'jarvis':   return '🧠 Jarvis';
    case 'hermes':   return '📡 Hermes';
    case 'openclaw': return '🦅 OpenClaw';
    case 'harvey':   return '⚖️ Harvey';
    default:         return 'M0Claw';
  }
}

function agentGreeting(agent?: AgentName | null): string {
  switch (agent) {
    case 'jarvis':
      return [
        '🧠 Jarvis online.',
        '',
        'Was steht heute an?',
        '',
        '/status  - System-Status',
        '/hermes  - Hermes Bus-Status',
        '/help    - Alle Befehle',
      ].join('\n');
    case 'hermes':
      return [
        '📡 Hermes — System Status Channel',
        '',
        'Dieser Topic ist für automatische System-Alerts reserviert.',
        'Kein Smalltalk — nur Maschinen-Output.',
        '',
        '/status - Hermes Bus-Status',
      ].join('\n');
    case 'openclaw':
      return [
        '🦅 OpenClaw — Execution Engine',
        '',
        'Schick mir Tasks:',
        '• Content erstellen (Tweets, X-Posts, Artikel)',
        '• Code generieren',
        '• YouTube-Skripte',
        '• Browser-Actions',
        '',
        '/help - Alle Befehle',
      ].join('\n');
    case 'harvey':
      return [
        '⚖️ Harvey – Dein KI-Rechtsassistent',
        '',
        'Ich analysiere Verträge, AGBs und Rechtsdokumente.',
        '',
        'So geht\'s:',
        '1. Schick mir ein PDF, DOCX oder TXT',
        '2. Ich analysiere Risiken, Klauseln, Empfehlung',
        '3. Du bekommst deine Rechtsanalyse in Sekunden',
        '',
        '/review    - Dokument analysieren',
        '/credits   - Kostenlose Analysen anzeigen',
        '/subscribe - Premium freischalten',
        '',
        '2 kostenlose Analysen. Dann /subscribe.',
      ].join('\n');
    default:
      return [
        'M0Claw - Dein KI-Agent',
        '',
        'Schreib mir einfach - ich antworte mit KI.',
        'Links/Content → automatischer Promo-Post',
        '',
        '/clear - Chat zuruecksetzen',
        '/status - System-Status',
        '/models - Ollama Models',
        '/exec <cmd> - Shell Command',
        '/help - Alle Befehle',
      ].join('\n');
  }
}

function agentHelp(agent?: AgentName | null): string {
  switch (agent) {
    case 'jarvis':
      return [
        '🧠 Jarvis Befehle:',
        '',
        '/start   - Willkommen',
        '/status  - Bot-Status',
        '/hermes  - Hermes Bus + Goal-Status',
        '/clear   - Chat zurücksetzen',
        '/models  - Ollama Models',
        '/ping    - Pong',
        '/exec <cmd> - Shell (Admin)',
        '/help    - Diese Hilfe',
        '',
        'Oder einfach schreiben — Jarvis antwortet!',
      ].join('\n');
    case 'openclaw':
      return [
        '🦅 OpenClaw Befehle:',
        '',
        '/start   - Willkommen',
        '/status  - Bot-Status',
        '/hermes  - Hermes Bus-Status',
        '/ping    - Pong',
        '/help    - Diese Hilfe',
        '',
        'Task-Beispiele:',
        '  Schreib 10 Tweets zu KI-News',
        '  Generiere ein YouTube-Skript zu Ollama',
        '  Suche nach Infos zu OpenClaw',
      ].join('\n');
    case 'harvey':
      return [
        '⚖️ Harvey – KI-Rechtsassistent',
        '',
        'Dokument-Analyse:',
        '  Einfach PDF / DOCX / TXT schicken',
        '  → Vollständige Rechtsanalyse in Sekunden',
        '',
        'Befehle:',
        '/review    - Anleitung zur Dokument-Analyse',
        '/credits   - Verbleibende Analysen anzeigen',
        '/subscribe - Harvey Premium freischalten',
        '/paid      - Premium nach Zahlung aktivieren',
        '/clear     - Chat zurücksetzen',
        '/status    - Bot-Status',
        '/help      - Diese Hilfe',
        '',
        'Oder einfach deine Rechtsfrage schreiben!',
      ].join('\n');
    default:
      return [
        'M0Claw Befehle:',
        '',
        '/start - Willkommen',
        '/clear - Chat loeschen',
        '/status - Bot-Status',
        '/ping - Pong',
        '/models - Ollama Models',
        '/exec <cmd> - Shell ausfuehren',
        '/system - System-Info',
        '/help - Diese Hilfe',
        '',
        'Oder einfach schreiben - KI antwortet!',
        'Links → Promo-Post mit Freigabe',
      ].join('\n');
  }
}

// ── Harvey Legal Review Flow ──────────────────────────────────────────────────

async function handleLegalReview(
  botToken: string,
  chatId: number,
  userId: number | undefined,
  localPath: string,
  fileName: string,
  mimeType?: string,
  threadId?: number,
) {
  if (!userId) {
    await sendReply(botToken, chatId, threadId, 'Benutzer-ID nicht erkannt. Bitte erneut senden.');
    return;
  }

  const access = checkAccess(userId);
  if (!access.canReview) {
    await sendReply(botToken, chatId, threadId, access.paywallMessage ?? 'Limit erreicht. /subscribe für Premium.');
    return;
  }

  const freeNote = !access.paid && access.freeRemaining > 0
    ? `\n\n(${access.freeRemaining - 1} kostenlose Analysen danach verbleibend)`
    : '';

  await sendReply(botToken, chatId, threadId, `Analysiere "${fileName}"... Das dauert 10-30 Sekunden.${freeNote}`);
  await sendTyping(botToken, chatId);

  try {
    const rawText = await extractTextFromFile(localPath, mimeType);

    if (rawText.startsWith('[') && rawText.endsWith(']')) {
      await sendReply(botToken, chatId, threadId, rawText);
      return;
    }

    if (rawText.trim().length < 50) {
      await sendReply(
        botToken, chatId, threadId,
        'Das Dokument enthält zu wenig Text für eine Analyse. Bitte PDF mit Textlayer einsenden (kein Scan).',
      );
      return;
    }

    const analysis = await analyzeLegalDocument(rawText, fileName);
    recordReview(userId);

    for (const chunk of splitMessage(analysis, 4000)) {
      await sendReply(botToken, chatId, threadId, chunk, 'Markdown');
    }

    const updatedAccess = checkAccess(userId);
    if (!updatedAccess.paid && updatedAccess.freeRemaining === 0) {
      await sendReply(botToken, chatId, threadId, [
        'Das war deine letzte kostenlose Analyse.',
        '',
        'Für weitere Analysen → /subscribe',
      ].join('\n'));
    }
  } catch (err: any) {
    console.error('[LegalReview] Error:', err.message);
    await sendReply(
      botToken, chatId, threadId,
      `Analyse fehlgeschlagen: ${err.message}\n\nBitte erneut versuchen oder Text direkt einfügen.`,
    );
  }
}

// ── Promo flow ────────────────────────────────────────────────────────────────

async function handlePromoFlow(
  botToken: string,
  chatId: number,
  urls: string[],
  content: string,
  threadId?: number,
) {
  const url = urls[0];
  const sourceText = content || (url ? `Inhalt von: ${url}` : 'Content');

  const promo = await generatePromo(sourceText, url);
  const promoId = `promo_${Date.now()}_${chatId}`;
  pendingPromos.set(promoId, { chatId, promo, url });

  const params: Record<string, any> = {
    chat_id: chatId,
    text: `Promo-Vorschlag:\n\n${promo}`,
    reply_markup: {
      inline_keyboard: [
        [
          { text: 'Freigeben',      callback_data: `approve:${promoId}` },
          { text: 'Neu generieren', callback_data: `regen:${promoId}` },
        ],
        [
          { text: 'Bearbeiten', callback_data: `edit:${promoId}` },
          { text: 'Verwerfen',  callback_data: `reject:${promoId}` },
        ],
      ],
    },
  };
  if (threadId !== undefined) params.message_thread_id = threadId;

  await callTelegramApi(botToken, 'sendMessage', params);
}

// ── Callback query handler ────────────────────────────────────────────────────

async function handleCallbackQuery(botToken: string, callback: any) {
  const data      = callback.data || '';
  const chatId    = callback.message?.chat?.id;
  const threadId  = callback.message?.message_thread_id as number | undefined;

  if (!chatId) return;

  const colonIdx = data.indexOf(':');
  const action   = colonIdx >= 0 ? data.slice(0, colonIdx) : data;
  const promoId  = colonIdx >= 0 ? data.slice(colonIdx + 1) : '';
  const promoData = pendingPromos.get(promoId);

  await callTelegramApi(botToken, 'answerCallbackQuery', { callback_query_id: callback.id }).catch(() => {});

  switch (action) {
    case 'approve': {
      if (!promoData) {
        await sendReply(botToken, chatId, threadId, 'Promo nicht mehr verfuegbar.');
        return;
      }
      if (TARGET_CHANNEL) {
        try {
          await callTelegramApi(botToken, 'sendMessage', {
            chat_id: TARGET_CHANNEL,
            text: promoData.promo,
            disable_web_page_preview: false,
          });
          await sendReply(botToken, chatId, threadId, 'Promo gepostet in Channel!');
        } catch (err: any) {
          await sendReply(
            botToken, chatId, threadId,
            `Post-Fehler: ${err.message}\n\nPrüfe ob der Bot Admin im Channel ist.`,
          );
        }
      } else {
        await sendReply(
          botToken, chatId, threadId,
          'Freigegeben! (Kein Ziel-Channel konfiguriert)\n\nSetze TELEGRAM_TARGET_CHANNEL in .env',
        );
      }
      pendingPromos.delete(promoId);
      break;
    }

    case 'regen': {
      if (!promoData) return;
      await sendTyping(botToken, chatId);
      const newPromo = await generatePromo(promoData.promo, promoData.url);
      promoData.promo = newPromo;

      const params: Record<string, any> = {
        chat_id: chatId,
        text: `Neuer Vorschlag:\n\n${newPromo}`,
        reply_markup: {
          inline_keyboard: [
            [
              { text: 'Freigeben',      callback_data: `approve:${promoId}` },
              { text: 'Neu generieren', callback_data: `regen:${promoId}` },
            ],
            [
              { text: 'Bearbeiten', callback_data: `edit:${promoId}` },
              { text: 'Verwerfen',  callback_data: `reject:${promoId}` },
            ],
          ],
        },
      };
      if (threadId !== undefined) params.message_thread_id = threadId;
      await callTelegramApi(botToken, 'sendMessage', params);
      break;
    }

    case 'edit': {
      await sendReply(botToken, chatId, threadId, 'Schick mir den bearbeiteten Text - ich poste ihn dann.');
      break;
    }

    case 'reject': {
      pendingPromos.delete(promoId);
      await sendReply(botToken, chatId, threadId, 'Promo verworfen.');
      break;
    }
  }
}

// ── Utilities ─────────────────────────────────────────────────────────────────

function splitMessage(text: string, maxLen: number): string[] {
  if (text.length <= maxLen) return [text];
  const chunks: string[] = [];
  let remaining = text;
  while (remaining.length > 0) {
    if (remaining.length <= maxLen) {
      chunks.push(remaining);
      break;
    }
    let splitAt = remaining.lastIndexOf('\n', maxLen);
    if (splitAt < maxLen / 2) splitAt = maxLen;
    chunks.push(remaining.substring(0, splitAt));
    remaining = remaining.substring(splitAt).trimStart();
  }
  return chunks;
}

function mediaEmoji(type: string): string {
  const map: Record<string, string> = {
    photo: '[Foto]', video: '[Video]', document: '[Datei]', audio: '[Audio]',
    voice: '[Sprach]', video_note: '[VideoMsg]', sticker: '[Sticker]', animation: '[GIF]',
  };
  return map[type] ?? '[Medien]';
}

// ── Polling loop ──────────────────────────────────────────────────────────────

async function pollUpdates(botToken: string) {
  let offset = 0;

  try {
    const pending = await callTelegramApi(botToken, 'getUpdates', { offset: -1, limit: 1, timeout: 0 });
    if (pending.length > 0) offset = pending[pending.length - 1].update_id + 1;
  } catch (_) {}

  // Determine active persona label for logs
  const topicInfo = [
    TOPIC_JARVIS   !== undefined ? `jarvis→${TOPIC_JARVIS}`     : '',
    TOPIC_HERMES   !== undefined ? `hermes→${TOPIC_HERMES}`     : '',
    TOPIC_OPENCLAW !== undefined ? `openclaw→${TOPIC_OPENCLAW}` : '',
    TOPIC_HARVEY   !== undefined ? `harvey→${TOPIC_HARVEY}`     : '',
  ].filter(Boolean).join(', ');

  const persona = process.env.BOT_PERSONA;
  const modeStr = topicInfo
    ? `forum-routing [${topicInfo}]`
    : persona
      ? `single-persona (${persona})`
      : 'legacy M0Claw';

  const providerInfo = process.env.OLLAMA_BASE_URL
    ? `Ollama @ ${process.env.OLLAMA_BASE_URL}`
    : process.env.ANTHROPIC_API_KEY
      ? 'Anthropic'
      : process.env.OPENAI_API_KEY
        ? `Groq/OpenAI @ ${process.env.AI_API_BASE || 'openai'}`
        : 'KEIN PROVIDER';

  console.log(`[${new Date().toISOString()}] Core4 Telegram Bot — mode: ${modeStr}`);
  console.log(`Model   : ${process.env.AI_MODEL || 'standard'}`);
  console.log(`Provider: ${providerInfo}`);
  console.log(`Jarvis  : ${JARVIS_URL}`);
  console.log(`Hermes  : ${HERMES_URL}`);

  while (true) {
    try {
      const updates = await callTelegramApi(botToken, 'getUpdates', {
        offset,
        limit: 100,
        timeout: 30,
        allowed_updates: ['message', 'callback_query'],
      });

      for (const update of updates) {
        offset = update.update_id + 1;

        if (update.callback_query) {
          try {
            await handleCallbackQuery(botToken, update.callback_query);
          } catch (err: any) {
            console.error(`Callback error:`, err.message);
          }
        } else if (update.message) {
          try {
            await handleMessage(botToken, update.message);
          } catch (err: any) {
            console.error(`Message error ${update.update_id}:`, err.message);
          }
        }
      }
    } catch (err: any) {
      console.error(`[${new Date().toISOString()}] Poll error: ${err.message}`);
      await new Promise((r) => setTimeout(r, 5000));
    }
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

const botToken = process.env.TELEGRAM_BOT_TOKEN;

if (!botToken) {
  console.error('TELEGRAM_BOT_TOKEN is required.');
  process.exit(1);
}

console.log('Starting Core4 Telegram Bot...');
pollUpdates(botToken).catch((err) => {
  console.error('Fatal:', err);
  process.exit(1);
});
