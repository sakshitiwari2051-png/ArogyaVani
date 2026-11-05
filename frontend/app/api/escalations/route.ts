import { NextResponse } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

export const revalidate = 0;

const STATUSES = ['open', 'acknowledged', 'resolved'];

function openDb() {
  const dbPath =
    process.env.SQLITE_DB_PATH || path.resolve(process.cwd(), '../backend/data/helpline.db');
  if (!fs.existsSync(dbPath)) return null;
  const db = new DatabaseSync(dbPath);
  db.exec('PRAGMA busy_timeout = 3000');
  return db;
}

const ref = (id: number) => `ESC-${String(id).padStart(4, '0')}`;

function verifyAdminAuth(req: Request): boolean {
  const expected = process.env.ADMIN_TOKEN || process.env.LIVEKIT_API_SECRET;
  if (expected) {
    const adminHeader = req.headers.get('x-admin-token');
    if (adminHeader && adminHeader === expected) return true;

    const authHeader = req.headers.get('authorization') || '';
    if (authHeader.startsWith('Bearer ') && authHeader.slice(7) === expected) return true;

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
  // Enforce server-side authentication for patient escalation records
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
    const db = openDb();
    if (!db)
      return NextResponse.json({ escalations: [] }, { headers: { 'Cache-Control': 'no-store' } });

    try {
      // Audit log authorized escalation data access
      console.info(
        `[AUDIT] Authorized escalation records retrieved at ${new Date().toISOString()} (filter: ${status})`
      );

      // Strictly project clinical escalation fields matching backend db.py schema
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

      const rows = status ? query.all(status) : query.all();
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
        .get(id);
      return NextResponse.json({ escalation: { ...row, ref: ref(id) } });
    } finally {
      db.close();
    }
  } catch (error) {
    console.error('Escalations PATCH error:', error);
    return NextResponse.json({ error: 'internal error' }, { status: 500 });
  }
}
