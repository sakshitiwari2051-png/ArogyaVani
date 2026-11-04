export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'ArogyaVani Health Helpline',
  pageTitle: 'ArogyaVani — AI Health Access Platform',
  pageDescription: 'Sovereign Indic Voice AI Health Helpline, powered by Gnani.ai (Prisma STT, Timbre TTS, Evon LLM) & LiveKit',

  // Voice-only on purpose: this models a phone call to a health centre.
  supportsChatInput: true,

  logo: '/arogyavani.png',
  accent: '#0D9488',
  logoDark: '/arogyavani.png',
  accentDark: '#2DD4BF',
  startButtonText: 'Call ArogyaVani',

  // agent dispatch configuration
  agentName: process.env.AGENT_NAME ?? undefined,

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,
};
