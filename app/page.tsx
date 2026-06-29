import AgentCard from "@/components/AgentCard";
import ActivityFeed from "@/components/ActivityFeed";
import { getRecentActivity } from "@/lib/activity";

export default async function DashboardPage() {
  const activity = await getRecentActivity(10);

  return (
    <div className="space-y-8">
      <section>
        <h2 className="font-display text-3xl mb-2">Dashboard</h2>
        <p className="text-delix-ink/60">
          Three agents handling your social posts, product sync, and customer DMs.
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <AgentCard
          name="Social Media Poster"
          href="/social"
          accent="rose"
          description="Drafts and schedules posts for Facebook, Instagram, and TikTok."
          actions={["Generate post", "Schedule", "Review queue"]}
        />
        <AgentCard
          name="Shopify Product Sync"
          href="/shopify"
          accent="gold"
          description="Pulls products from Shopify, writes descriptions, syncs back."
          actions={["Pull catalog", "Generate copy", "Push updates"]}
        />
        <AgentCard
          name="DM Reply Agent"
          href="/inbox"
          accent="ink"
          description="Reads incoming FB & TikTok messages (including images) and replies."
          actions={["Incoming inbox", "Auto-reply rules"]}
        />
      </section>

      <section>
        <h3 className="font-display text-2xl mb-3">Recent activity</h3>
        <ActivityFeed items={activity} />
      </section>
    </div>
  );
}
