import { Hero } from "@/components/Hero";
import { Stats } from "@/components/sections/Stats";
import { CategoryBento } from "@/components/sections/CategoryBento";
import { FeaturedProducts } from "@/components/sections/FeaturedProducts";
import { RepairShowcase } from "@/components/sections/RepairShowcase";
import { WhyUs } from "@/components/sections/WhyUs";
import { Testimonials } from "@/components/sections/Testimonials";
import { CtaBanner } from "@/components/sections/CtaBanner";
import { readProducts } from "@/lib/store";

export const dynamic = "force-dynamic";

export default async function Home() {
  const products = await readProducts();
  const featured = [...products].sort(
    (a, b) => Number(b.featured) - Number(a.featured),
  );

  return (
    <>
      <Hero />
      <Stats />
      <CategoryBento />
      <FeaturedProducts products={featured} />
      <RepairShowcase />
      <WhyUs />
      <Testimonials />
      <CtaBanner />
    </>
  );
}
