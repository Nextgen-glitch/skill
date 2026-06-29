export const integrationMode = (): "mock" | "live" =>
  process.env.INTEGRATION_MODE === "live" ? "live" : "mock";

export function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var: ${name}`);
  return v;
}
