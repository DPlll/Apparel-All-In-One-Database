import { fetchProducts, fetchBrands } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import FilterSidebar from "@/components/FilterSidebar";
import Link from "next/link";
import type { ProductFilters } from "@/types/product";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<Record<string, string | undefined>>;
}

export default async function CatalogPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const page = Number(params.page ?? 1);

  const filters: ProductFilters = {
    brand: params.brand,
    style: params.style as ProductFilters["style"],
    color: params.color,
    size: params.size,
    sort: params.sort as ProductFilters["sort"],
    page,
  };

  const [productsData, brands] = await Promise.all([
    fetchProducts(filters),
    fetchBrands(),
  ]);

  const { items, total, per_page } = productsData;
  const totalPages = Math.ceil(total / per_page);

  function buildPageUrl(p: number) {
    const urlParams = new URLSearchParams(
      Object.fromEntries(
        Object.entries({ ...params, page: String(p) }).filter(
          ([, v]) => v !== undefined
        ) as [string, string][]
      )
    );
    return `/catalog?${urlParams.toString()}`;
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="font-serif text-3xl text-stone-900 mb-8">All Swimwear</h1>
      <div className="flex flex-col lg:flex-row gap-10">
        <FilterSidebar brands={brands} />
        <div className="flex-1">
          {items.length === 0 ? (
            <div className="text-center py-24 text-stone-400">
              <p className="font-serif text-xl mb-4">No products found.</p>
              <Link href="/catalog" className="text-[11px] uppercase tracking-widest text-rose-400 hover:text-rose-600 transition-colors">
                Clear filters
              </Link>
            </div>
          ) : (
            <>
              <p className="text-[11px] uppercase tracking-widest text-stone-400 mb-6">{total} products</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-x-4 gap-y-10">
                {items.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
              {totalPages > 1 && (
                <div className="mt-14 flex justify-center items-center gap-4">
                  {page > 1 && (
                    <Link href={buildPageUrl(page - 1)} className="text-xs uppercase tracking-widest text-stone-500 hover:text-rose-500 transition-colors">
                      ← Prev
                    </Link>
                  )}
                  <span className="text-xs text-stone-400">{page} / {totalPages}</span>
                  {page < totalPages && (
                    <Link href={buildPageUrl(page + 1)} className="text-xs uppercase tracking-widest text-stone-500 hover:text-rose-500 transition-colors">
                      Next →
                    </Link>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
