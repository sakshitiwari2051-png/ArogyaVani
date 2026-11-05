import { NextResponse } from 'next/server';
import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

export const revalidate = 0;

export async function POST(req: Request) {
  try {
    const cookieHeader = req.headers.get('cookie') || '';
    const cookieMatch = cookieHeader.match(/arogyavani_caller_id=([^;]+)/);
    const callerId = cookieMatch ? cookieMatch[1] : null;

    const body = await req.json().catch(() => ({}));
    const targetId = body?.user_id || callerId;
    const targetName = body?.name;

    if (!targetId && !targetName) {
      return NextResponse.json(
        {
          error: 'Valid caller identification (cookie or user_id) is required to execute deletion.',
        },
        { status: 400 }
      );
    }

    const dbPath =
      process.env.SQLITE_DB_PATH || path.resolve(process.cwd(), '../backend/data/helpline.db');

    let deletedCallers = 0;
    let deletedEscalations = 0;

    if (fs.existsSync(dbPath)) {
      try {
        const db = new DatabaseSync(dbPath);
        db.exec('PRAGMA foreign_keys = ON');

        // Cascade delete from both callers AND related escalations to prevent orphaned clinical data
        if (targetId && targetName) {
          const res1 = db
            .prepare('DELETE FROM callers WHERE user_id = ? OR LOWER(name) = LOWER(?) OR name = ?')
            .run(targetId, targetName, targetName);
          deletedCallers = Number(res1.changes);

          const res2 = db
            .prepare(
              'DELETE FROM escalations WHERE caller_user_id = ? OR LOWER(caller_name) = LOWER(?)'
            )
            .run(targetId, targetName);
          deletedEscalations = Number(res2.changes);
        } else if (targetId) {
          const res1 = db.prepare('DELETE FROM callers WHERE user_id = ?').run(targetId);
          deletedCallers = Number(res1.changes);

          const res2 = db.prepare('DELETE FROM escalations WHERE caller_user_id = ?').run(targetId);
          deletedEscalations = Number(res2.changes);
        } else if (targetName) {
          const res1 = db
            .prepare('DELETE FROM callers WHERE LOWER(name) = LOWER(?) OR name = ?')
            .run(targetName, targetName);
          deletedCallers = Number(res1.changes);

          const res2 = db
            .prepare('DELETE FROM escalations WHERE LOWER(caller_name) = LOWER(?)')
            .run(targetName);
          deletedEscalations = Number(res2.changes);
        }

        db.close();
        console.info(
          `[AUDIT] Memory wipe executed for target '${targetId || targetName}': ${deletedCallers} callers, ${deletedEscalations} escalations purged.`
        );
      } catch (dbErr) {
        console.error('Error executing cascade deletion in SQLite:', dbErr);
      }
    }

    const headers = new Headers({
      'Cache-Control': 'no-store',
      'Set-Cookie': 'arogyavani_caller_id=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax',
    });

    return NextResponse.json(
      {
        success: true,
        message: 'Personal profile and associated escalation records permanently purged.',
        records_purged: { callers: deletedCallers, escalations: deletedEscalations },
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
