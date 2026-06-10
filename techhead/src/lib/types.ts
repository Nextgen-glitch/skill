export type Category =
  | "Smartphones"
  | "Tablets"
  | "Smartwatches"
  | "Audio"
  | "Smart Home"
  | "Accessories";

export const CATEGORIES: Category[] = [
  "Smartphones",
  "Tablets",
  "Smartwatches",
  "Audio",
  "Smart Home",
  "Accessories",
];

export type Condition = "New" | "Refurbished";

export interface Product {
  id: string;
  name: string;
  brand: string;
  category: Category;
  condition: Condition;
  price: number;
  originalPrice?: number | null;
  description: string;
  specs: string[];
  image?: string | null; // path under /public or remote URL; null => styled placeholder
  rating: number; // 0..5
  reviews: number;
  stock: number;
  featured?: boolean;
  createdAt: string;
}

export interface RepairService {
  id: string;
  title: string;
  blurb: string;
  from: number;
  turnaround: string;
}
