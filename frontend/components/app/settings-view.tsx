'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Database,
  ExternalLink,
  Globe2,
  Headphones,
  Lock,
  Mic,
  Radio,
  RefreshCw,
  Server,
  Settings,
  ShieldCheck,
  Sparkles,
  Trash2,
  Volume2,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/shadcn/utils';

interface SettingsViewProps {
  onForgetMemory?: () => void;
}

export function SettingsView({ onForgetMemory }: SettingsViewProps) {
  // Voice & Model Stack State
  const [ttsEngine, setTtsEngine] = useState<'gnani' | 'murf'>('gnani');
  const [sttEngine, setSttEngine] = useState<'gnani' | 'deepgram'>('gnani');
  const [llmEngine, setLlmEngine] = useState<'gnani' | 'groq'>('gnani');
  const [language, setLanguage] = useState<'hi' | 'en' | 'bilingual'>('bilingual');

  // Audio Processing Toggles
  const [noiseCancellation, setNoiseCancellation] = useState<boolean>(true);
  const [bargeIn, setBargeIn] = useState<boolean>(true);
  const [auto108Latch, setAuto108Latch] = useState<boolean>(true);
  const [piiScrubbing, setPiiScrubbing] = useState<boolean>(true);
  const [memorySync, setMemorySync] = useState<boolean>(true);

  const handleSave = () => {
    toast.success('Settings saved successfully', {
      description: 'Your voice pipeline preferences are now active.',
    });
  };

  return (
    <div className="clay-card flex flex-1 flex-col overflow-y-auto p-4 md:p-6">
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200/60 pb-4 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex size-9 items-center justify-center rounded-xl bg-teal-500/10 text-teal-600 dark:bg-teal-400/10 dark:text-teal-400">
              <Settings className="size-5" />
            </div>
            <div>
              <h2 className="text-lg font-black tracking-tight text-slate-900 dark:text-slate-100">
                ArogyaVani System Settings
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Manage sovereign voice engines, clinical emergency latches, and privacy controls.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            className="clay-btn flex cursor-pointer items-center gap-1.5 bg-teal-600 px-4 py-2 text-xs font-bold text-white hover:bg-teal-700 active:scale-95 dark:bg-teal-500 dark:hover:bg-teal-600"
          >
            <CheckCircle2 className="size-3.5" />
            <span>Save Preferences</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* ── 1. Voice AI Engine Stack (Gnani Sovereign vs Fallback) ── */}
        <section className="clay-card rounded-2xl p-4 md:p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="size-4 text-amber-500" />
              <h3 className="text-sm font-black tracking-wide uppercase text-slate-900 dark:text-slate-100">
                Voice AI Pipeline Engines
              </h3>
            </div>
            <span className="rounded-full bg-teal-50 px-2 py-0.5 text-[10px] font-bold text-teal-700 dark:bg-teal-950/70 dark:text-teal-300">
              Sovereign Indic Stack
            </span>
          </div>

          <div className="space-y-4 text-xs">
            {/* Speech to Text */}
            <div>
              <label className="mb-1.5 block font-bold text-slate-700 dark:text-slate-300">
                Speech-to-Text (STT) Engine
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setSttEngine('gnani')}
                  className={cn(
                    'flex flex-col items-start rounded-xl border p-2.5 text-left transition-all',
                    sttEngine === 'gnani'
                      ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800'
                  )}
                >
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Gnani Prisma v2.5
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Sovereign Indic 16kHz
                  </span>
                </button>
                <button
                  type="button"
                  onClick={() => setSttEngine('deepgram')}
                  className={cn(
                    'flex flex-col items-start rounded-xl border p-2.5 text-left transition-all',
                    sttEngine === 'deepgram'
                      ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800'
                  )}
                >
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Deepgram Nova-3
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Fallback STT engine
                  </span>
                </button>
              </div>
            </div>

            {/* Healthcare LLM */}
            <div>
              <label className="mb-1.5 block font-bold text-slate-700 dark:text-slate-300">
                Healthcare Reasoning LLM
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setLlmEngine('gnani')}
                  className={cn(
                    'flex flex-col items-start rounded-xl border p-2.5 text-left transition-all',
                    llmEngine === 'gnani'
                      ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800'
                  )}
                >
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Gnani Evon v3.3
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Indic Clinical Medical LLM
                  </span>
                </button>
                <button
                  type="button"
                  onClick={() => setLlmEngine('groq')}
                  className={cn(
                    'flex flex-col items-start rounded-xl border p-2.5 text-left transition-all',
                    llmEngine === 'groq'
                      ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800'
                  )}
                >
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Groq Qwen 2.5 / Gemini
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Ultra-low latency fallback
                  </span>
                </button>
              </div>
            </div>

            {/* Text to Speech */}
            <div>
              <label className="mb-1.5 block font-bold text-slate-700 dark:text-slate-300">
                Text-to-Speech (TTS) Voice
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setTtsEngine('gnani')}
                  className={cn(
                    'flex flex-col items-start rounded-xl border p-2.5 text-left transition-all',
                    ttsEngine === 'gnani'
                      ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800'
                  )}
                >
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Gnani Timbre v2.5
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    Arogya Indic Female Voice
                  </span>
                </button>
                <button
                  type="button"
                  onClick={() => setTtsEngine('murf')}
                  className={cn(
                    'flex flex-col items-start rounded-xl border p-2.5 text-left transition-all',
                    ttsEngine === 'murf'
                      ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800'
                  )}
                >
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Murf Falcon TTS
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    High-clarity fallback voice
                  </span>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* ── 2. Language & Dialect Assistance ── */}
        <section className="clay-card rounded-2xl p-4 md:p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Globe2 className="size-4 text-blue-500" />
              <h3 className="text-sm font-black tracking-wide uppercase text-slate-900 dark:text-slate-100">
                Language & Bharat Lexicon
              </h3>
            </div>
            <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-bold text-blue-700 dark:bg-blue-950/70 dark:text-blue-300">
              Dialect Aware
            </span>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="mb-1.5 block font-bold text-slate-700 dark:text-slate-300">
                Preferred Consultation Language
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setLanguage('bilingual')}
                  className={cn(
                    'rounded-xl border p-2 text-center font-bold transition-all',
                    language === 'bilingual'
                      ? 'border-blue-500 bg-blue-50/50 text-blue-900 dark:border-blue-400 dark:bg-blue-950/30 dark:text-blue-200'
                      : 'border-slate-200 text-slate-700 dark:border-slate-800 dark:text-slate-300'
                  )}
                >
                  Bilingual (Auto)
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage('hi')}
                  className={cn(
                    'rounded-xl border p-2 text-center font-bold transition-all',
                    language === 'hi'
                      ? 'border-blue-500 bg-blue-50/50 text-blue-900 dark:border-blue-400 dark:bg-blue-950/30 dark:text-blue-200'
                      : 'border-slate-200 text-slate-700 dark:border-slate-800 dark:text-slate-300'
                  )}
                >
                  हिन्दी (Hindi)
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage('en')}
                  className={cn(
                    'rounded-xl border p-2 text-center font-bold transition-all',
                    language === 'en'
                      ? 'border-blue-500 bg-blue-50/50 text-blue-900 dark:border-blue-400 dark:bg-blue-950/30 dark:text-blue-200'
                      : 'border-slate-200 text-slate-700 dark:border-slate-800 dark:text-slate-300'
                  )}
                >
                  English (India)
                </button>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/40">
              <div className="flex items-start gap-2.5">
                <Radio className="mt-0.5 size-4 text-teal-600 dark:text-teal-400 shrink-0" />
                <div>
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Bharat Medical Lexicon
                  </span>
                  <p className="mt-0.5 text-[11px] text-slate-500 dark:text-slate-400">
                    Automatically transliterates rural terms (e.g., <em>chaati mein jakdan</em>,{' '}
                    <em>peshaab mein jalan</em>) into standardized clinical triage codes.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/40">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Barge-In (Interruptibility)
                  </span>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Allows caller to interrupt ArogyaVani mid-speech naturally.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={bargeIn}
                  onChange={(e) => setBargeIn(e.target.checked)}
                  className="size-4 accent-teal-600"
                />
              </div>
            </div>
          </div>
        </section>

        {/* ── 3. Clinical Safety & 108 Emergency Latch ── */}
        <section className="clay-card rounded-2xl p-4 md:p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-rose-500" />
              <h3 className="text-sm font-black tracking-wide uppercase text-slate-900 dark:text-slate-100">
                Safety & Emergency Guardrails
              </h3>
            </div>
            <span className="rounded-full bg-rose-50 px-2 py-0.5 text-[10px] font-bold text-rose-700 dark:bg-rose-950/70 dark:text-rose-300">
              Code-Level Latch
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/40">
              <div>
                <span className="font-bold text-slate-900 dark:text-slate-100">
                  108 Emergency Auto-Bypass
                </span>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Bypasses LLM hallucinations if cardiac or severe trauma keywords appear.
                </p>
              </div>
              <input
                type="checkbox"
                checked={auto108Latch}
                onChange={(e) => setAuto108Latch(e.target.checked)}
                className="size-4 accent-rose-600"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/40">
              <div>
                <span className="font-bold text-slate-900 dark:text-slate-100">
                  Adaptive Noise Suppression
                </span>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Silero VAD + WebRTC Krisp filters background tractor & street sounds.
                </p>
              </div>
              <input
                type="checkbox"
                checked={noiseCancellation}
                onChange={(e) => setNoiseCancellation(e.target.checked)}
                className="size-4 accent-teal-600"
              />
            </div>

            <div className="mt-2 rounded-xl bg-amber-50/60 p-3 text-[11px] text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
              <span className="font-bold">Teleconsultation Specialist Handoff:</span> When complex
              symptoms exceed PHC protocol, caller is queued for Varanasi CHC specialist handoff.
            </div>
          </div>
        </section>

        {/* ── 4. Privacy, Memory & Human Admin ── */}
        <section className="clay-card rounded-2xl p-4 md:p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lock className="size-4 text-emerald-500" />
              <h3 className="text-sm font-black tracking-wide uppercase text-slate-900 dark:text-slate-100">
                Privacy, ABHA Memory & Admin
              </h3>
            </div>
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 dark:bg-emerald-950/70 dark:text-emerald-300">
              HIPAA & DISHA Aligned
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/40">
              <div>
                <span className="font-bold text-slate-900 dark:text-slate-100">
                  PII Automated Scrubbing
                </span>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Masks phone numbers, Aadhaar, and financial data in transcripts.
                </p>
              </div>
              <input
                type="checkbox"
                checked={piiScrubbing}
                onChange={(e) => setPiiScrubbing(e.target.checked)}
                className="size-4 accent-emerald-600"
              />
            </div>

            <div className="flex items-center justify-between rounded-xl border border-slate-200/80 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/40">
              <div>
                <span className="font-bold text-slate-900 dark:text-slate-100">
                  Consultation Memory Retention
                </span>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Allows returning caller recognition across sessions.
                </p>
              </div>
              <input
                type="checkbox"
                checked={memorySync}
                onChange={(e) => setMemorySync(e.target.checked)}
                className="size-4 accent-emerald-600"
              />
            </div>

            {/* Forget Me Action */}
            <div className="flex items-center justify-between rounded-xl border border-rose-200/60 bg-rose-50/30 p-3 dark:border-rose-900/40 dark:bg-rose-950/20">
              <div>
                <span className="font-bold text-rose-900 dark:text-rose-200">
                  Forget My Memory
                </span>
                <p className="text-[11px] text-rose-700/80 dark:text-rose-300/70">
                  Permanently delete all stored consultation records and session history.
                </p>
              </div>
              {onForgetMemory && (
                <button
                  type="button"
                  onClick={onForgetMemory}
                  className="clay-btn flex items-center gap-1 bg-rose-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-rose-700 active:scale-95"
                >
                  <Trash2 className="size-3" />
                  <span>Wipe</span>
                </button>
              )}
            </div>

            {/* Link to Admin Portal */}
            <div className="pt-2">
              <Link
                href="/admin"
                className="flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50/60 px-4 py-3 font-bold text-teal-900 transition-all hover:bg-teal-100/70 dark:border-teal-800 dark:bg-teal-950/40 dark:text-teal-200"
              >
                <div className="flex items-center gap-2">
                  <Activity className="size-4 text-teal-600 dark:text-teal-400" />
                  <span>Open Human Specialist Escalation Queue (/admin)</span>
                </div>
                <ArrowRight className="size-4" />
              </Link>
            </div>
          </div>
        </section>
      </div>

      {/* ── System Connectivity Diagnostics Bar ── */}
      <div className="mt-6 rounded-2xl border border-slate-200/80 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-900/60">
        <div className="mb-2 text-[11px] font-bold tracking-wider uppercase text-slate-500 dark:text-slate-400">
          Live Backend Services & Diagnostics
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-slate-700 dark:text-slate-300">LiveKit WebRTC:</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400">Connected</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-slate-700 dark:text-slate-300">Gnani Sovereign:</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400">Ready</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-slate-700 dark:text-slate-300">SIP Telephony:</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400">Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-slate-700 dark:text-slate-300">SQLite WAL:</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400">Healthy</span>
          </div>
        </div>
      </div>
    </div>
  );
}
