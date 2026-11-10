import { NextResponse } from 'next/server';

export const revalidate = 0;

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const lat = Number(body?.lat);
    const lon = Number(body?.lon);

    if (isNaN(lat) || isNaN(lon)) {
      return NextResponse.json(
        { error: 'Invalid coordinates provided' },
        { status: 400 }
      );
    }

    let district = 'Varanasi';
    let city = 'Varanasi';
    let suburb = 'Shivpur';
    let state = 'Uttar Pradesh';
    let pincode = '221002';
    let formatted = 'Shivpur, Varanasi, Uttar Pradesh 221002';

    try {
      const osmRes = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`,
        {
          headers: {
            'User-Agent': 'ArogyaVaniHealthVoiceAgent/1.0 (health-access@arogyavani.org)',
            Accept: 'application/json',
          },
          next: { revalidate: 3600 },
        }
      );

      if (osmRes.ok) {
        const data = await osmRes.json();
        const addr = data.address || {};
        district =
          addr.state_district ||
          addr.district ||
          addr.county ||
          addr.city ||
          addr.town ||
          district;
        city = addr.city || addr.town || addr.village || addr.suburb || city;
        suburb = addr.suburb || addr.neighbourhood || addr.quarter || suburb;
        state = addr.state || state;
        pincode = addr.postcode || pincode;
        formatted =
          data.display_name ||
          `${suburb ? suburb + ', ' : ''}${city}, ${state} ${pincode}`;
      }
    } catch (err) {
      console.warn('OSM reverse geocoding exception (using fallback):', err);
    }

    const locationData = {
      lat,
      lon,
      district,
      city,
      suburb,
      state,
      pincode,
      formatted,
    };

    const res = NextResponse.json({ success: true, location: locationData });
    res.cookies.set('arogyavani_location', JSON.stringify(locationData), {
      path: '/',
      maxAge: 30 * 24 * 3600,
      sameSite: 'lax',
    });

    return res;
  } catch (error) {
    console.error('Location API error:', error);
    return NextResponse.json(
      { error: 'Failed to process location' },
      { status: 500 }
    );
  }
}
