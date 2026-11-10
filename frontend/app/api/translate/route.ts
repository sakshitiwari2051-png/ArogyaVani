import { NextRequest, NextResponse } from 'next/server';

const BHASHINI_USER_ID = process.env.BHASHINI_USER_ID || '1c951803fedd46b7be1d0b2e86fa7105';
const BHASHINI_API_KEY = process.env.BHASHINI_API_KEY || '28b2f8853c-3826-4256-9b24-0e1a733feee7';
const BHASHINI_INFERENCE_KEY =
  process.env.BHASHINI_INFERENCE_KEY ||
  'nJhuL08q3SCLUCPKF_S37jMtKcA2SfSLZ8XmYJcJ1xxyyDIUHiER87T06vnXTA8V';

export async function POST(req: NextRequest) {
  try {
    const { text, sourceLang = 'en', targetLang = 'hi' } = await req.json();

    if (!text || !text.trim()) {
      return NextResponse.json({ translatedText: '' });
    }

    if (sourceLang === targetLang) {
      return NextResponse.json({ translatedText: text });
    }

    // Call Government of India Bhashini Dhruva NMT (IndicTrans2)
    const payload = {
      pipelineTasks: [
        {
          taskType: 'translation',
          config: {
            language: {
              sourceLanguage: sourceLang,
              targetLanguage: targetLang,
            },
            serviceId: 'ai4bharat/indictrans-v2-all-gpu--t4',
          },
        },
      ],
      inputData: {
        input: [{ source: text }],
      },
    };

    const res = await fetch('https://dhruva-api.bhashini.gov.in/services/inference/pipeline', {
      method: 'POST',
      headers: {
        Authorization: BHASHINI_INFERENCE_KEY,
        'Content-Type': 'application/json',
        userID: BHASHINI_USER_ID,
        ulcaApiKey: BHASHINI_API_KEY,
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      const data = await res.json();
      const output = data?.pipelineResponse?.[0]?.output?.[0]?.target;
      if (output) {
        return NextResponse.json({ translatedText: output, provider: 'Bhashini IndicTrans2' });
      }
    }

    return NextResponse.json({ translatedText: text, provider: 'passthrough' });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Translation error';
    return NextResponse.json({ error: message, translatedText: '' }, { status: 500 });
  }
}

