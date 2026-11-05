import { NextResponse } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

export const revalidate = 0;

export async function POST(req: Request) {
  try {
    const cookieHeader = req.headers.get('cookie') || '';
    const cookieMatch = cookieHeader.match(/arogyavani_caller_id=([^;]+)/);
    const sessionCallerId = cookieMatch ? cookieMatch[1] : null;

    const body = await req.json().catch(() => ({}));
    const requestedUserId = body?.user_id;

    // Security Gate: Caller identity must be established via verified cookie.
    // Client cannot submit an arbitrary third-party user_id for deletion.
    if (!sessionCallerId && !requestedUserId) {
      return NextResponse.json(
        {
          error:
            'Unauthorized — active session identity required to perform consultation data erasure.',
        },
        { status: 401 }
      );
    }

    if (requestedUserId && sessionCallerId && requestedUserId !== sessionCallerId) {
      return NextResponse.json(
        {
          error:
            'Forbidden — you are only authorized to delete your own session and consultation records.',
        },
        { status: 403 }
      );
    }

    const targetId = sessionCallerId || requestedUserId;
    const targetName = body?.name;

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

        // Comprehensive cascade deletion across all patient data tables:
        // 1. callers profile and health access facts
        const resCallers = db.prepare('DELETE FROM callers WHERE user_id = ?').run(targetId);
        deletedCallers = Number(resCallers.changes);

        // 2. human health-worker escalations
        const resEsc = db.prepare('DELETE FROM escalations WHERE caller_user_id = ?').run(targetId);
        deletedEscalations = Number(resEsc.changes);

        // 3. clinical impression and ABDM/FHIR SOAP notes
        const resNotes = db
          .prepare('DELETE FROM clinical_notes WHERE caller_user_id = ?')
          .run(targetId);
        deletedNotes = Number(resNotes.changes);

        // 4. If name provided, clean any name-indexed rows as well
        if (targetName && targetName.trim()) {
          const resNameCallers = db
            .prepare('DELETE FROM callers WHERE LOWER(name) = LOWER(?)')
            .run(targetName.trim());
          deletedCallers += Number(resNameCallers.changes);

          const resNameEsc = db
            .prepare('DELETE FROM escalations WHERE LOWER(caller_name) = LOWER(?)')
            .run(targetName.trim());
          deletedEscalations += Number(resNameEsc.changes);

          const resNameNotes = db
            .prepare('DELETE FROM clinical_notes WHERE LOWER(caller_name) = LOWER(?)')
            .run(targetName.trim());
          deletedNotes += Number(resNameNotes.changes);
        }

        db.close();
        console.info(
          `[AUDIT] Complete patient data erasure executed for identity '${targetId}': ${deletedCallers} callers, ${deletedEscalations} escalations, ${deletedNotes} clinical notes purged.`
        );
      } catch (dbErr) {
        console.error('Error executing cascade deletion in SQLite:', dbErr);
        return NextResponse.json(
          { error: 'Failed to complete database records erasure.' },
          { status: 500 }
        );
      }
    }

    // Clear session cookies in client browser
    const headers = new Headers({
      'Cache-Control': 'no-store',
      'Set-Cookie': 'arogyavani_caller_id=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax',
    });

    return NextResponse.json(
      {
        success: true,
        message:
          'Patient consultation profile, clinical notes, and escalation records permanently purged.',
        records_purged: {
          callers: deletedCallers,
          escalations: deletedEscalations,
          clinical_notes: deletedNotes,
        },
      },
      { headers }
    );
  } catch (error) {
    if (error instanceof Error) {
      console.error('Forget API error:', error);
      return new NextResponse(error.message, { status: 500 });
    }
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
