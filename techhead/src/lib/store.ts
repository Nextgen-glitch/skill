import { promises as fs } from "fs";
import path from "path";
import type { Product } from "./types";

// Simple JSON-file backed store. Good enough for a demo/admin panel;
// swap for a real DB (Postgres, SQLite, etc.) in production.
const DATA_FILE = path.join(process.cwd(), "src", "data", "products.json");

export async function readProducts(): Promise<Product[]> {
  try {
    const raw = await fs.readFile(DATA_FILE, "utf-8");
    return JSON.parse(raw) as Product[];
  } catch {
    return [];
  }
}

export async function writeProducts(products: Product[]): Promise<void> {
  await fs.writeFile(DATA_FILE, JSON.stringify(products, null, 2), "utf-8");
}

export async function getProduct(id: string): Promise<Product | undefined> {
  const products = await readProducts();
  return products.find((p) => p.id === id);
}

export function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 40);
}
