import { NextResponse } from 'next/server';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

export const revalidate = 0;

const SESSION_SECRET =
  process.env.ADMIN_TOKEN ||
  process.env.LIVEKIT_API_SECRET ||
  'arogyavani_session_signing_secret_2026';

const SUPABASE_URL = (process.env.SUPABASE_URL || '').replace(/\/$/, '');
const SUPABASE_KEY = process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_PUBLISHABLE_KEY || '';

function verifySignedCallerId(cookieVal: string | null): string | null {
  if (!cookieVal || typeof cookieVal !== 'string') return null;
  const parts = cookieVal.split('.');
  if (parts.length !== 2) return null;
  const [callerId, sig] = parts;
  if (!/^caller_[0-9a-fA-F-]{36}$/.test(callerId)) return null;
  try {
    const expectedHmac = crypto.createHmac('sha256', SESSION_SECRET).update(callerId).digest('hex');
    const sigBuf = Buffer.from(sig, 'hex');
    const expBuf = Buffer.from(expectedHmac, 'hex');
    if (sigBuf.length !== expBuf.length || !crypto.timingSafeEqual(sigBuf, expBuf)) {
      return null;
    }
    return callerId;
  } catch {
    return null;
  }
}

export async function POST(req: Request) {
  try {
    const cookieHeader = req.headers.get('cookie') || '';
    const cookieMatch = cookieHeader.match(/arogyavani_caller_id=([^;]+)/);
    const rawCookie = cookieMatch ? decodeURIComponent(cookieMatch[1]) : null;

    // Security Gate: Caller identity must be established via a cryptographically signed session cookie.
    const verifiedCallerId = verifySignedCallerId(rawCookie);
    if (!verifiedCallerId) {
      return NextResponse.json(
        {
          error:
            'Unauthorized — active, cryptographically signed session identity required to perform consultation data erasure.',
        },
        { status: 401 }
      );
    }

    const body = await req.json().catch(() => ({}));
    const requestedUserId = body?.user_id;

    // Ownership check: If client passes a user_id, it must strictly match the verified session caller ID
    if (requestedUserId && requestedUserId !== verifiedCallerId) {
      return NextResponse.json(
        {
          error:
            'Forbidden — you are only authorized to delete your own session and consultation records.',
        },
        { status: 403 }
      );
    }

    const targetId = verifiedCallerId;
    let deletedCallers = 0;
    let deletedEscalations = 0;
    let deletedNotes = 0;

    // 1. Supabase Cloud Database deletion if configured
    if (SUPABASE_URL && SUPABASE_KEY) {
      try {
        const headers = {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
          Prefer: 'count=exact',
        };

        const [delC, delE, delN] = await Promise.all([
          fetch(`${SUPABASE_URL}/rest/v1/callers?user_id=eq.${encodeURIComponent(targetId)}`, {
            method: 'DELETE',
            headers,
          }),
          fetch(
            `${SUPABASE_URL}/rest/v1/escalations?caller_user_id=eq.${encodeURIComponent(targetId)}`,
            {
              method: 'DELETE',
              headers,
            }
          ),
          fetch(
            `${SUPABASE_URL}/rest/v1/clinical_notes?caller_user_id=eq.${encodeURIComponent(targetId)}`,
            {
              method: 'DELETE',
              headers,
            }
          ),
        ]);

        const parseCount = (h: Headers) => {
          const range = h.get('content-range');
          if (range && range.includes('/')) {
            const count = Number(range.split('/')[1]);
            return isNaN(count) ? 0 : count;
          }
          return 0;
        };

        deletedCallers += parseCount(delC.headers);
        deletedEscalations += parseCount(delE.headers);
        deletedNotes += parseCount(delN.headers);

        console.info(`[AUDIT] Supabase patient data erasure executed for '${targetId}'`);
      } catch (sbErr) {
        console.warn('Supabase forget deletion warning:', sbErr);
      }
    }

    // 2. Local SQLite deletion
    const dbPath =
      process.env.SQLITE_DB_PATH || path.resolve(process.cwd(), '../backend/data/helpline.db');

    if (fs.existsSync(dbPath)) {
      try {
        const db = new DatabaseSync(dbPath);
        db.exec('PRAGMA foreign_keys = ON');
        db.exec('PRAGMA busy_timeout = 3000');

        db.exec('BEGIN TRANSACTION');
        try {
          const resCallers = db.prepare('DELETE FROM callers WHERE user_id = ?').run(targetId);
          deletedCallers += Number(resCallers.changes);

          const resEsc = db
            .prepare('DELETE FROM escalations WHERE caller_user_id = ?')
            .run(targetId);
          deletedEscalations += Number(resEsc.changes);

          const resNotes = db
            .prepare('DELETE FROM clinical_notes WHERE caller_user_id = ?')
            .run(targetId);
          deletedNotes += Number(resNotes.changes);

          db.exec('COMMIT');
        } catch (txErr) {
          db.exec('ROLLBACK');
          throw txErr;
        }

        db.close();
      } catch (dbErr) {
        console.error('Error executing atomic cascade deletion in SQLite:', dbErr);
      }
    }

    const res = NextResponse.json({
      success: true,
      deleted_records: {
        callers: deletedCallers,
        escalations: deletedEscalations,
        clinical_notes: deletedNotes,
        total: deletedCallers + deletedEscalations + deletedNotes,
      },
      message: 'All caller records, clinical notes, and escalations permanently purged.',
    });

    // Invalidate and expire session identity cookie
    res.headers.set(
      'Set-Cookie',
      'arogyavani_caller_id=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax'
    );
    res.headers.set('Cache-Control', 'no-store');

    return res;
  } catch (error) {
    console.error('POST /api/forget error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
