import { PrismaClient } from "@prisma/client";
import { generateDecisions, generateIncidents, generateSessions } from "../src/app/lib/mockData";

const prisma = new PrismaClient();

async function main() {
  console.log("Seeding database with production-grade mock data...");

  // Generate data using our deterministic mock module
  const decisions = generateDecisions(200);
  const incidents = generateIncidents();
  const sessions = generateSessions();

  // 1. Seed Sessions
  console.log(`Seeding ${sessions.length} sessions...`);
  for (const session of sessions) {
    await prisma.session.upsert({
      where: { session_id: session.session_id },
      update: session,
      create: session,
    });
  }

  // 2. Add some parameters
  const defaultParams = {
    confidence_threshold: 0.7,
    phonetic_threshold: 0.85,
    lambda: 1.2,
    min_improvement: 0.5,
    hot_words: JSON.stringify(["gaussian", "eigen", "convolutional", "markov"]),
    whisper_model: "large-v3",
    lm_model: "domain-specific-n-gram",
  };

  for (const session of sessions) {
    await prisma.parameter.upsert({
      where: { session_id: session.session_id },
      update: defaultParams,
      create: {
        session_id: session.session_id,
        ...defaultParams,
      },
    });
  }

  // 3. Clear existing decisions and seed new ones
  console.log("Clearing existing decisions and incidents...");
  await prisma.incident.deleteMany({});
  await prisma.decision.deleteMany({});

  console.log(`Seeding ${decisions.length} decisions...`);
  // Note: generateDecisions provides `id`s, we'll strip them out to let DB sequence handle it,
  // but keep track of mapping for incidents. Actually, we can just insert them directly but remove `id`
  const decisionMap = new Map();
  
  for (const d of decisions) {
    const { id, timestamp, ...rest } = d;
    const created = await prisma.decision.create({
      data: {
        ...rest,
        timestamp: new Date(timestamp),
      },
    });
    decisionMap.set(id, created.id);
  }

  // 4. Seed Incidents mapping to the new DB IDs
  console.log(`Seeding ${incidents.length} incidents...`);
  for (const incident of incidents) {
    const { id, timestamp, decision_id, ...rest } = incident;
    const realDecisionId = decisionMap.get(decision_id);
    
    // Only insert if matching decision exists in our seed
    if (realDecisionId) {
      await prisma.incident.create({
        data: {
          ...rest,
          timestamp: new Date(timestamp),
          decision_id: realDecisionId,
        },
      });
    }
  }

  console.log("✅ Database seeding complete. Ready for production demonstration.");
}

main()
  .catch((e) => {
    console.error("Error seeding database:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
