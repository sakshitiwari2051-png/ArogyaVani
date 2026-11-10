import { NextRequest, NextResponse } from 'next/server';

const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID || '';
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN || '';
const TWILIO_PHONE_NUMBER = process.env.TWILIO_PHONE_NUMBER || '+17372508034';

const DEFAULT_TWIML = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="hi-IN">नमस्ते! मैं आरोग्यवाणी स्वास्थ्य सेवा हूँ।</Say>
    <Say voice="Polly.Kajal" language="en-IN">Welcome to ArogyaVani sovereign voice health helpline.</Say>
    <Pause length="1"/>
    <Say voice="Polly.Aditi" language="hi-IN">यदि आपको कोई आपातकालीन समस्या है, जैसे सीने में तेज दर्द, सांस लेने में तकलीफ, या बेहोशी, तो कृपया बिना देरी किए तुरंत 108 एम्बुलेंस पर कॉल करें। सामान्य परामर्श और निशुल्क दवाओं के लिए अपने नजदीकी प्राथमिक स्वास्थ्य केंद्र या जन औषधि केंद्र जाएं।</Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="en-IN">For acute emergencies, dial 108 immediately. Thank you for connecting with ArogyaVani. Stay safe and healthy!</Say>
</Response>`;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    let rawPhone = (body.phone || '').trim().replace(/[\s()-]/g, '');

    if (!rawPhone) {
      return NextResponse.json(
        { error: 'Phone number is required' },
        { status: 400 }
      );
    }

    // Auto-prefix Indian numbers (+91) if entered as 10 digits
    if (/^\d{10}$/.test(rawPhone)) {
      rawPhone = `+91${rawPhone}`;
    } else if (!rawPhone.startsWith('+')) {
      rawPhone = `+${rawPhone}`;
    }

    if (!TWILIO_ACCOUNT_SID || !TWILIO_AUTH_TOKEN) {
      return NextResponse.json(
        { error: 'Twilio telephony credentials are not configured on the server.' },
        { status: 500 }
      );
    }

    const authHeader = `Basic ${Buffer.from(`${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}`).toString('base64')}`;

    const formData = new URLSearchParams();
    formData.append('To', rawPhone);
    formData.append('From', TWILIO_PHONE_NUMBER);
    formData.append('Twiml', DEFAULT_TWIML);

    const res = await fetch(
      `https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Calls.json`,
      {
        method: 'POST',
        headers: {
          Authorization: authHeader,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      }
    );

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        {
          error: data.message || 'Twilio call failed',
          code: data.code,
          details: data,
        },
        { status: res.status }
      );
    }

    return NextResponse.json({
      success: true,
      sid: data.sid,
      status: data.status,
      to: rawPhone,
      message: `Call initiated to ${rawPhone}. Your phone should ring shortly!`,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
