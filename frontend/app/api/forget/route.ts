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
    // An attacker cannot forge an arbitrary caller ID or delete third-party health records.
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
    const dbPath =
      process.env.SQLITE_DB_PATH || path.resolve(process.cwd(), '../backend/data/helpline.db');

    let deletedCallers = 0;
    let deletedEscalations = 0;
    let deletedNotes = 0;

    if (fs.existsSync(dbPath)) {
      try {
        const db = new DatabaseSync(dbPath);
        db.exec('PRAGMA foreign_keys = ON');
        db.exec('PRAGMA busy_timeout = 3000');

        // Comprehensive atomic cascade deletion across all patient data tables:
        // Bound strictly to verified caller identity (no global name-based deletions to avoid name collision risks)
        db.exec('BEGIN TRANSACTION');
        try {
          // 1. callers profile and health access facts
          const resCallers = db.prepare('DELETE FROM callers WHERE user_id = ?').run(targetId);
          deletedCallers = Number(resCallers.changes);

          // 2. human health-worker escalations
          const resEsc = db
            .prepare('DELETE FROM escalations WHERE caller_user_id = ?')
            .run(targetId);
          deletedEscalations = Number(resEsc.changes);

          // 3. clinical impression and ABDM/FHIR SOAP notes
          const resNotes = db
            .prepare('DELETE FROM clinical_notes WHERE caller_user_id = ?')
            .run(targetId);
          deletedNotes = Number(resNotes.changes);

          db.exec('COMMIT');
        } catch (txErr) {
          db.exec('ROLLBACK');
          throw txErr;
        }

        db.close();
        console.info(
          `[AUDIT] Complete atomic patient data erasure executed for identity '${targetId}': ${deletedCallers} callers, ${deletedEscalations} escalations, ${deletedNotes} clinical notes purged.`
        );
      } catch (dbErr) {
        console.error('Error executing atomic cascade deletion in SQLite:', dbErr);
        return NextResponse.json(
          { error: 'Failed to complete database records erasure.' },
          { status: 500 }
        );
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
