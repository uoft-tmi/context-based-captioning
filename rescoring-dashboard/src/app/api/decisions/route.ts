import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// This API route handles incoming logs from the python rescoring engine
export async function POST(request: Request) {
  try {
    const data = await request.json();
    const { table, ...payload } = data;

    if (table === 'sessions') {
      const session = await prisma.session.upsert({
        where: { session_id: payload.session_id },
        update: payload,
        create: payload,
      });
      return NextResponse.json({ success: true, data: session });
    }

    if (table === 'parameters') {
      const param = await prisma.parameter.upsert({
        where: { session_id: payload.session_id },
        update: payload,
        create: payload,
      });
      return NextResponse.json({ success: true, data: param });
    }

    if (table === 'decisions') {
      const decision = await prisma.decision.create({
        data: payload,
      });
      return NextResponse.json({ success: true, data: decision });
    }

    if (table === 'session_update') {
      const session = await prisma.session.update({
        where: { session_id: payload.session_id },
        data: {
          total_words: payload.total_words,
          low_confidence_words: payload.low_confidence_words,
          words_rescored: payload.words_rescored,
          wer_before: payload.wer_before,
          wer_after: payload.wer_after,
          processing_time: payload.processing_time,
        },
      });
      return NextResponse.json({ success: true, data: session });
    }

    return NextResponse.json({ error: 'Invalid table specified' }, { status: 400 });
  } catch (error: any) {
    console.error('Error in /api/decisions POST:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// Fetch all decisions for the dashboard UI
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');
  const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 100;

  try {
    const decisions = await prisma.decision.findMany({
      where: action && action !== 'All' ? { action } : undefined,
      take: limit,
      orderBy: { timestamp: 'desc' },
    });
    return NextResponse.json({ decisions });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
