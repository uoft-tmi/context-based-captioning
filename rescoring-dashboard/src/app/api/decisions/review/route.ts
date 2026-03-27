import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function PATCH(request: Request) {
  try {
    const data = await request.json();
    const { id, user_approved, flagged, user_feedback } = data;

    if (!id) {
      return NextResponse.json({ error: 'Decision ID required' }, { status: 400 });
    }

    const updated = await prisma.decision.update({
      where: { id: parseInt(id) },
      data: {
        user_approved: user_approved !== undefined ? user_approved : undefined,
        flagged: flagged !== undefined ? flagged : undefined,
        user_feedback: user_feedback !== undefined ? user_feedback : undefined,
      },
    });

    return NextResponse.json({ success: true, decision: updated });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
