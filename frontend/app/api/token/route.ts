import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import crypto from 'node:crypto';
import { RoomConfiguration } from '@livekit/protocol';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;
const AGENT_NAME = process.env.AGENT_NAME;
const SESSION_SECRET =
  process.env.ADMIN_TOKEN ||
  process.env.LIVEKIT_API_SECRET ||
  'arogyavani_session_signing_secret_2026';

function signCallerId(callerId: string): string {
  const hmac = crypto.createHmac('sha256', SESSION_SECRET).update(callerId).digest('hex');
  return `${callerId}.${hmac}`;
}

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

// Rate limiting in-memory map: IP -> timestamp list
const rateLimitMap = new Map<string, number[]>();
const RATE_LIMIT_WINDOW_MS = 60_000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 30; // Max 30 tokens per min per IP

function isRateLimited(ip: string): boolean {
  const now = Date.now();
  const timestamps = rateLimitMap.get(ip) || [];
  const validTimestamps = timestamps.filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  if (validTimestamps.length >= MAX_REQUESTS_PER_WINDOW) {
    return true;
  }
  validTimestamps.push(now);
  rateLimitMap.set(ip, validTimestamps);
  return false;
}

export const revalidate = 0;

export async function POST(req: Request) {
  try {
    if (!LIVEKIT_URL) throw new Error('LIVEKIT_URL is not defined');
    if (!API_KEY) throw new Error('LIVEKIT_API_KEY is not defined');
    if (!API_SECRET) throw new Error('LIVEKIT_API_SECRET is not defined');

    const clientIp =
      req.headers.get('x-forwarded-for')?.split(',')[0].trim() ||
      req.headers.get('x-real-ip') ||
      '127.0.0.1';

    if (isRateLimited(clientIp)) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Too many session token requests.' },
        { status: 429, headers: { 'Retry-After': '60' } }
      );
    }

    const body = await req.json().catch(() => ({}));
    let roomConfig: RoomConfiguration | undefined;
    if (body?.room_config) {
      roomConfig = RoomConfiguration.fromJson(body.room_config, { ignoreUnknownFields: true });
    } else if (AGENT_NAME) {
      roomConfig = RoomConfiguration.fromJson(
        { agents: [{ agentName: AGENT_NAME }] },
        { ignoreUnknownFields: true }
      );
    }

    const cookieHeader = req.headers.get('cookie') || '';
    const cookieMatch = cookieHeader.match(/arogyavani_caller_id=([^;]+)/);
    const existingRawCookie = cookieMatch ? decodeURIComponent(cookieMatch[1]) : null;

    const participantName = body?.participant_name || body?.name || 'Caller';
    // Security: Caller identity is cryptographically signed with HMAC to prevent caller impersonation.
    // Client cannot supply arbitrary existing caller identities or forge cookie values.
    const verifiedCallerId = verifySignedCallerId(existingRawCookie);
    const participantIdentity = verifiedCallerId || `caller_${crypto.randomUUID()}`;
    const signedSessionCookie = signCallerId(participantIdentity);

    const langCookieMatch = cookieHeader.match(/arogyavani_lang=([^;]+)/);
    const lang =
      body?.language ||
      new URL(req.url, 'http://localhost').searchParams.get('lang') ||
      (langCookieMatch ? langCookieMatch[1] : null) ||
      'hi';

    const locCookieMatch = cookieHeader.match(/arogyavani_location=([^;]+)/);
    let userLoc = null;
    if (locCookieMatch) {
      try {
        userLoc = JSON.parse(decodeURIComponent(locCookieMatch[1]));
      } catch {}
    }
    if (!userLoc && body?.location) {
      userLoc = body.location;
    }

    const roomName = `voice_assistant_room_${crypto.randomUUID().slice(0, 8)}`;

    const participantToken = await createParticipantToken(
      {
        identity: participantIdentity,
        name: participantName,
        metadata: JSON.stringify({
          language: lang,
          source: 'web',
          location: userLoc,
        }),
      },
      roomName,
      roomConfig
    );

    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantName,
      participantToken,
    };

    const headers = new Headers({
      'Cache-Control': 'no-store',
      // Cryptographically signed, HttpOnly cookie prevents client-side tampering, forgery, or XSS leakage
      'Set-Cookie': `arogyavani_caller_id=${encodeURIComponent(
        signedSessionCookie
      )}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax`,
    });

    return NextResponse.json(data, { headers });
  } catch (error) {
    if (error instanceof Error) {
      console.error('LiveKit Token API error:', error);
      return new NextResponse(error.message, { status: 500 });
    }
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}

function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string,
  roomConfig?: RoomConfiguration
): Promise<string> {
  const at = new AccessToken(API_KEY, API_SECRET, {
    ...userInfo,
    ttl: '15m',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  if (roomConfig) {
    at.roomConfig = roomConfig;
  }

  return at.toJwt();
}
