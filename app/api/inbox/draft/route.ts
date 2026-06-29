import { NextResponse } from "next/server";
import { z } from "zod";
import { getInbox, draftReply } from "@/lib/agents/inbox";

const Schema = z.object({ id: z.string() });

export async function POST(req: Request) {
  try {
    const { id } = Schema.parse(await req.json());
    const { messages } = await getInbox();
    const dm = messages.find((m) => m.id === id);
    if (!dm) return new NextResponse("Not found", { status: 404 });
    const reply = await draftReply(dm);
    return NextResponse.json(reply);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Failed";
    return new NextResponse(msg, { status: 400 });
  }
}
