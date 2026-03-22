import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    // Basic aggregate metrics
    const totalDecisions = await prisma.decision.count();
    const rescored = await prisma.decision.count({ where: { action: 'replaced' } });
    
    // Approval rate
    const reviewed = await prisma.decision.count({ where: { user_approved: { not: null } } });
    const approved = await prisma.decision.count({ where: { user_approved: true } });
    const approvalRate = reviewed > 0 ? (approved / reviewed) * 100 : 0;

    // We can't use grouped sums easily in edge runtime Prisma without some specific edge packages, 
    // but count() works. Realistically for exact totals in sessions we might fetch sessions.
    
    return NextResponse.json({
      totalDecisions,
      rescored,
      approvalRate: approvalRate.toFixed(1),
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
