import { notFound } from "next/navigation";
import { fetchBrands, fetchProducts } from "@/lib/api";
import ProductCard from "@/components/ProductCard";

export const dynamic = "force-dynamic";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function BrandPage({ params }: PageProps) {
  const { slug } = await params;

  const [brands, productsData] = await Promise.all([
    fetchBrands(),
    fetchProducts({ brand: slug }),
  ]);

  const brand = brands.find((b) => b.brand_slug === slug);
  if (!brand) notFound();

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="mb-10 pb-8 border-b border-sand-200">
        <h1 className="font-serif text-4xl text-stone-900">{brand.brand}</h1>
        <p className="text-[11px] uppercase tracking-widest text-stone-400 mt-2">
          {brand.product_count} products
        </p>
      </div>

      {productsData.items.length === 0 ? (
        <p className="text-stone-400 text-center py-20">No products available.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-10">
          {productsData.items.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
