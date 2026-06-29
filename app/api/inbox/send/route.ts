import { NextResponse } from "next/server";
import { z } from "zod";
import { getInbox, sendReply } from "@/lib/agents/inbox";

const Schema = z.object({ id: z.string(), text: z.string().min(1) });

export async function POST(req: Request) {
  try {
    const { id, text } = Schema.parse(await req.json());
    const { messages } = await getInbox();
    const dm = messages.find((m) => m.id === id);
    if (!dm) return new NextResponse("Not found", { status: 404 });
    const result = await sendReply(dm, text);
    return NextResponse.json(result);
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Failed";
    return new NextResponse(msg, { status: 400 });
  }
}
