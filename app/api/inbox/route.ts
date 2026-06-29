import { NextResponse } from "next/server";
import { getInbox } from "@/lib/agents/inbox";

export async function GET() {
  const data = await getInbox();
  return NextResponse.json(data);
}
