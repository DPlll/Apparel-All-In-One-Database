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
      <section className="relative pt-28 pb-24 px-4 text-center overflow-hidden bg-vintage-50">
        {/* Warm radial glow */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,_#F4C5AF33_0%,_transparent_70%)] pointer-events-none" />

        <p className="relative text-[11px] uppercase tracking-[0.3em] text-terra-500 mb-6 font-medium">
          Summer &#x2767; The best in women&apos;s swimwear
        </p>
        <h1 className="relative font-serif text-5xl sm:text-6xl lg:text-8xl text-drift-900 leading-[1.05] mb-7">
          Every brand.<br className="hidden sm:block" />
          <em className="not-italic text-terra-500">One place.</em>
        </h1>
        <p className="relative text-sm text-drift-400 mb-10 max-w-xs mx-auto leading-relaxed tracking-wide">
          Browse top swimwear labels and shop directly on their site.
        </p>
        <Link
          href="/catalog"
          className="relative inline-block px-10 py-3.5 bg-terra-500 text-vintage-50 text-xs tracking-[0.2em] uppercase hover:bg-terra-600 transition-colors duration-200 rounded-sm"
        >
          Shop All
        </Link>
      </section>

      {/* Divider */}
      <div className="h-px bg-vintage-200 mx-6" />

      {/* Brands strip */}
      <section className="max-w-5xl mx-auto px-6 py-12">
        <p className="text-[10px] uppercase tracking-[0.3em] text-drift-400 mb-6 text-center">
          Featured Brands
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {brands.map((b) => (
            <Link
              key={b.brand_slug}
              href={`/brands/${b.brand_slug}`}
              className="px-4 py-1.5 border border-vintage-300 text-xs tracking-wide text-drift-600 hover:border-terra-400 hover:text-terra-500 hover:bg-terra-100 transition-all rounded-full"
            >
              {b.brand}
            </Link>
          ))}
        </div>
      </section>

      {/* New arrivals */}
      <section className="max-w-5xl mx-auto px-6 pb-24">
        <div className="flex items-baseline justify-between mb-8">
          <h2 className="font-serif text-2xl text-drift-900">New Arrivals</h2>
          <Link href="/catalog" className="text-[11px] uppercase tracking-widest text-drift-400 hover:text-terra-500 transition-colors">
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
