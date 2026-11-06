import { NextResponse } from 'next/server';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

export const revalidate = 0;

const STATUSES = ['open', 'acknowledged', 'resolved'];

interface EscalationRow {
  id: number | string;
  caller_user_id: string;
  caller_name?: string;
  language?: string;
  urgency?: string;
  what_happened: string;
  already_checked?: string;
  followup_method?: string;
  callback_phone?: string;
  status: string;
  resolution_note?: string;
  created_at?: string;
  updated_at?: string;
}

const SUPABASE_URL = (process.env.SUPABASE_URL || '').replace(/\/$/, '');
const SUPABASE_KEY =
  process.env.SUPABASE_SECRET_KEY ||
  process.env.SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  '';

function openDb() {
  const dbPath =
    process.env.SQLITE_DB_PATH || path.resolve(process.cwd(), '../backend/data/helpline.db');
  if (!fs.existsSync(dbPath)) return null;
  const db = new DatabaseSync(dbPath);
  db.exec('PRAGMA busy_timeout = 3000');
  return db;
}

const ref = (id: number) => `ESC-${String(id).padStart(4, '0')}`;

function timingSafeCompare(a: string, b: string): boolean {
  try {
    const bufA = Buffer.from(a, 'utf-8');
    const bufB = Buffer.from(b, 'utf-8');
    if (bufA.length !== bufB.length) return false;
    return crypto.timingSafeEqual(bufA, bufB);
  } catch {
    return false;
  }
}

function verifyAdminAuth(req: Request): boolean {
  const expected = process.env.ADMIN_TOKEN || process.env.LIVEKIT_API_SECRET;
  if (expected) {
    const adminHeader = req.headers.get('x-admin-token');
    if (adminHeader && timingSafeCompare(adminHeader, expected)) return true;

    const authHeader = req.headers.get('authorization') || '';
    if (authHeader.startsWith('Bearer ') && timingSafeCompare(authHeader.slice(7), expected)) {
      return true;
    }

    return false;
  }

  // Development localhost fallback if no ADMIN_TOKEN is set
  const host = req.headers.get('host') || '';
  if (
    process.env.NODE_ENV === 'development' &&
    (host.includes('localhost') || host.includes('127.0.0.1'))
  ) {
    return true;
  }

  return false;
}

export async function GET(req: Request) {
  // Enforce server-side constant-time authentication for patient escalation records
  if (!verifyAdminAuth(req)) {
    return NextResponse.json(
      {
        error:
          'unauthorized — valid admin token required via x-admin-token or Authorization Bearer',
      },
      { status: 401, headers: { 'Cache-Control': 'no-store' } }
    );
  }

  try {
    const status = new URL(req.url).searchParams.get('status') ?? 'open';

    // 1. Prioritize Cloud Supabase if configured (Production / Vercel ready)
    if (SUPABASE_URL && SUPABASE_KEY) {
      try {
        const queryParams = new URLSearchParams({
          select:
            'id,caller_user_id,caller_name,language,urgency,what_happened,already_checked,followup_method,callback_phone,status,resolution_note,created_at,updated_at',
          order: 'created_at.desc',
          limit: '100',
        });
        if (status && status !== 'all') {
          queryParams.set('status', `eq.${status}`);
        }

        const sbRes = await fetch(`${SUPABASE_URL}/rest/v1/escalations?${queryParams.toString()}`, {
          headers: {
            apikey: SUPABASE_KEY,
            Authorization: `Bearer ${SUPABASE_KEY}`,
          },
          cache: 'no-store',
        });

        if (sbRes.ok) {
          const rows = (await sbRes.json()) as EscalationRow[];
          const escalations = rows.map((r) => ({ ...r, ref: ref(Number(r.id)) }));
          console.info(
            `[AUDIT] Retrieved ${escalations.length} escalations from Supabase (filter: ${status})`
          );
          return NextResponse.json({ escalations }, { headers: { 'Cache-Control': 'no-store' } });
        }
      } catch (sbErr) {
        console.warn('Supabase fetch failed, falling back to local SQLite:', sbErr);
      }
    }

    // 2. Fallback to Local SQLite
    const db = openDb();
    if (!db)
      return NextResponse.json({ escalations: [] }, { headers: { 'Cache-Control': 'no-store' } });

    try {
      console.info(
        `[AUDIT] Authorized escalation records retrieved from SQLite at ${new Date().toISOString()} (filter: ${status})`
      );

      const query = status
        ? db.prepare(
            `SELECT id, caller_user_id, caller_name, language, urgency, what_happened, already_checked, followup_method, callback_phone, status, resolution_note, created_at, updated_at
             FROM escalations
             WHERE status = ?
             ORDER BY created_at DESC
             LIMIT 100`
          )
        : db.prepare(
            `SELECT id, caller_user_id, caller_name, language, urgency, what_happened, already_checked, followup_method, callback_phone, status, resolution_note, created_at, updated_at
             FROM escalations
             ORDER BY created_at DESC
             LIMIT 100`
          );

      const rows = (status ? query.all(status) : query.all()) as unknown as EscalationRow[];
      const escalations = rows.map((r) => ({ ...r, ref: ref(Number(r.id)) }));
      return NextResponse.json({ escalations }, { headers: { 'Cache-Control': 'no-store' } });
    } finally {
      db.close();
    }
  } catch (error) {
    console.error('Escalations GET error:', error);
    return NextResponse.json({ escalations: [] }, { headers: { 'Cache-Control': 'no-store' } });
  }
}

export async function PATCH(req: Request) {
  if (!verifyAdminAuth(req)) {
    return NextResponse.json(
      { error: 'forbidden — set ADMIN_TOKEN and send x-admin-token or Authorization Bearer' },
      { status: 403 }
    );
  }

  try {
    const body = await req.json().catch(() => ({}));
    const escRef = String(body?.ref ?? '');
    const status = String(body?.status ?? '').toLowerCase();
    const note = String(body?.note ?? '');
    const id = Number(escRef.replace(/\D/g, ''));
    if (!id || !STATUSES.includes(status)) {
      return NextResponse.json({ error: 'bad ref or status' }, { status: 400 });
    }

    // 1. Supabase PATCH
    if (SUPABASE_URL && SUPABASE_KEY) {
      try {
        const patchRes = await fetch(`${SUPABASE_URL}/rest/v1/escalations?id=eq.${id}`, {
          method: 'PATCH',
          headers: {
            apikey: SUPABASE_KEY,
            Authorization: `Bearer ${SUPABASE_KEY}`,
            'Content-Type': 'application/json',
            Prefer: 'return=representation',
          },
          body: JSON.stringify({
            status,
            resolution_note: note,
            updated_at: new Date().toISOString(),
          }),
        });

        if (patchRes.ok) {
          const updated = await patchRes.json();
          if (updated && updated.length > 0) {
            console.info(`[AUDIT] Escalation ${ref(id)} updated in Supabase to '${status}'`);
            return NextResponse.json({
              escalation: { ...updated[0], ref: ref(id) },
            });
          }
        }
      } catch (sbErr) {
        console.warn('Supabase PATCH failed, falling back to SQLite:', sbErr);
      }
    }

    // 2. Local SQLite PATCH
    const db = openDb();
    if (!db) return NextResponse.json({ error: 'database not found' }, { status: 404 });
    try {
      const res = db
        .prepare(
          'UPDATE escalations SET status = ?, resolution_note = ?, updated_at = ? WHERE id = ?'
        )
        .run(status, note, new Date().toISOString(), id);
      if (res.changes === 0) return NextResponse.json({ error: 'not found' }, { status: 404 });

      console.info(
        `[AUDIT] Escalation ${ref(id)} updated to '${status}' at ${new Date().toISOString()}`
      );

      const row = db
        .prepare(
          'SELECT id, caller_user_id, caller_name, language, urgency, what_happened, already_checked, followup_method, callback_phone, status, resolution_note, created_at, updated_at FROM escalations WHERE id = ?'
        )
        .get(id) as unknown as EscalationRow;
      return NextResponse.json({ escalation: { ...row, ref: ref(id) } });
    } finally {
      db.close();
    }
  } catch (error) {
    console.error('Escalations PATCH error:', error);
    return NextResponse.json({ error: 'internal error' }, { status: 500 });
  }
}
