import Link from "next/link";
import { fetchBrands, fetchProducts } from "@/lib/api";
import ProductCard from "@/components/ProductCard";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [brandsData, productsData] = await Promise.all([
    fetchBrands(),
    fetchProducts({ sort: "newest", page: 1 }),
  ]);

  const brands = brandsData.slice(0, 12);
  const newArrivals = productsData.items.slice(0, 8);

  return (
    <>
      {/* Hero */}
      <section className="pt-24 pb-20 px-4 text-center bg-sand-50">
        <p className="text-[11px] uppercase tracking-[0.25em] text-stone-400 mb-5">
          The best in women&apos;s swimwear
        </p>
        <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl text-stone-900 leading-tight mb-6">
          Every brand.<br className="hidden sm:block" /> One place.
        </h1>
        <p className="text-base text-stone-400 mb-10 max-w-sm mx-auto leading-relaxed">
          Browse top swimwear labels and shop directly on their site.
        </p>
        <Link
          href="/catalog"
          className="inline-block px-10 py-3 border border-stone-900 text-stone-900 text-xs tracking-widest uppercase hover:bg-stone-900 hover:text-white transition-colors duration-200"
        >
          Shop All
        </Link>
      </section>

      {/* Thin divider */}
      <div className="h-px bg-sand-200 mx-6" />

      {/* Brands strip */}
      <section className="max-w-5xl mx-auto px-6 py-12">
        <p className="text-[10px] uppercase tracking-[0.3em] text-stone-400 mb-6 text-center">
          Featured Brands
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {brands.map((b) => (
            <Link
              key={b.brand_slug}
              href={`/brands/${b.brand_slug}`}
              className="px-4 py-1.5 border border-sand-300 text-xs tracking-wide text-stone-600 hover:border-rose-400 hover:text-rose-500 transition-colors rounded-full"
            >
              {b.brand}
            </Link>
          ))}
        </div>
      </section>

      {/* New arrivals */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <div className="flex items-baseline justify-between mb-8">
          <h2 className="font-serif text-2xl text-stone-900">New Arrivals</h2>
          <Link href="/catalog" className="text-[11px] uppercase tracking-widest text-stone-400 hover:text-rose-500 transition-colors">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-8">
          {newArrivals.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>
    </>
  );
}
