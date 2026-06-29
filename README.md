# DELIX COSMETICS AGENT

A web app that runs three AI agents for your cosmetics brand:

1. **Social Media Poster** — drafts and publishes posts for Facebook, Instagram, and TikTok.
2. **Shopify Product Sync** — pulls your catalog, writes product descriptions, and pushes updates back.
3. **DM Reply Agent** — receives Facebook and TikTok messages (including images), drafts on-brand replies, and escalates to a human when needed.

Powered by **Claude Sonnet 4.6** via the Anthropic SDK. Built with Next.js 14 + TypeScript.

---

## Quick start

```bash
npm install
cp .env.example .env.local
# add your ANTHROPIC_API_KEY at minimum
npm run dev
```

Open http://localhost:3000.

The app ships with `INTEGRATION_MODE=mock`, so it works out of the box without Shopify or Meta credentials. The Inbox page has a "Seed sample messages" button so you can try the reply agent immediately.

---

## Going live

When you're ready to connect real APIs, flip `INTEGRATION_MODE=live` in `.env.local` and provide credentials. Each integration is independent — you can light them up one at a time.

### Shopify

1. In your Shopify admin, go to **Apps → Develop apps → Create an app**.
2. Configure Admin API scopes: `read_products`, `write_products`.
3. Install the app and copy the **Admin API access token**.
4. Set in `.env.local`:
   ```
   SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
   SHOPIFY_ADMIN_ACCESS_TOKEN=shpat_...
   ```

### Facebook / Instagram (Meta Graph API)

1. Create an app at https://developers.facebook.com.
2. Add the **Messenger** and **Instagram Graph API** products.
3. Generate a **Page Access Token** with `pages_messaging` and `pages_manage_posts` permissions.
4. In the Webhooks section, subscribe to `messages` and point the webhook URL at:
   ```
   https://your-domain.com/api/webhooks/facebook
   ```
   Use the value of `META_VERIFY_TOKEN` from your `.env.local` as the verify token.
5. Set in `.env.local`:
   ```
   META_PAGE_ID=
   META_PAGE_ACCESS_TOKEN=
   META_APP_SECRET=
   META_VERIFY_TOKEN=delix-verify-token-change-me
   ```

### TikTok

TikTok messaging requires approval through their developer portal. Once approved:

1. Get your `CLIENT_KEY`, `CLIENT_SECRET`, and a long-lived `ACCESS_TOKEN`.
2. Point the webhook URL at:
   ```
   https://your-domain.com/api/webhooks/tiktok
   ```
3. The exact payload shape depends on which TikTok product (Business / Shop / DMs) you were approved for — update the field extraction in `app/api/webhooks/tiktok/route.ts` to match your real payloads.

---

## Project structure

```
app/
  page.tsx                       Dashboard
  social/page.tsx                Social media composer
  shopify/page.tsx               Shopify sync UI
  inbox/page.tsx                 DM inbox
  api/
    social/draft, publish        Generate + publish posts
    shopify/products, generate-copy, update
    inbox, inbox/draft, inbox/send, inbox/seed
    webhooks/facebook            Meta webhook (verify + receive)
    webhooks/tiktok              TikTok webhook
lib/
  claude.ts                      Anthropic SDK wrapper
  activity.ts                    Activity log (in-memory ring buffer)
  env.ts                         Env helpers, integration-mode flag
  agents/
    social.ts                    Social agent logic
    shopify.ts                   Shopify agent logic
    inbox.ts                     DM reply agent (vision-enabled)
components/                      Shared UI
```

---

## Notes

- The activity log is an in-memory ring buffer for now. For production, swap it for Postgres or Redis — the interface in `lib/activity.ts` is small.
- DM webhooks call `draftReply()` asynchronously. For real traffic, push to a job queue instead of awaiting in the request handler.
- The TikTok send path is intentionally not implemented — TikTok's messaging API is gated behind approval and the endpoint depends on which product you're approved for.
- Image messages are handled by passing the image URL directly to Claude's vision API in `lib/agents/inbox.ts`.
