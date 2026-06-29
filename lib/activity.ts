// In-memory activity log. Swap for Postgres / Redis when ready for production.
// Keeps the most recent 200 entries.

export type AgentName = "social" | "shopify" | "inbox";

export interface ActivityEntry {
  id: string;
  agent: AgentName;
  message: string;
  ts: number;
  meta?: Record<string, unknown>;
}

const RING_SIZE = 200;
const ring: ActivityEntry[] = [];
let counter = 0;

export async function logActivity(
  agent: AgentName,
  message: string,
  meta?: Record<string, unknown>,
): Promise<ActivityEntry> {
  const entry: ActivityEntry = {
    id: `act_${++counter}`,
    agent,
    message,
    ts: Date.now(),
    meta,
  };
  ring.unshift(entry);
  if (ring.length > RING_SIZE) ring.length = RING_SIZE;
  return entry;
}

export async function getRecentActivity(limit = 20): Promise<ActivityEntry[]> {
  return ring.slice(0, limit);
}
