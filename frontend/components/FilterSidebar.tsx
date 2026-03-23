"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { Brand } from "@/types/product";

interface Props {
  brands: Brand[];
}

const STYLES = [
  { label: "Tops", value: "top" },
  { label: "Bottoms", value: "bottom" },
  { label: "Sets", value: "set" },
  { label: "One-Pieces", value: "one-piece" },
];

const SORT_OPTIONS = [
  { label: "Newest", value: "newest" },
  { label: "Price: Low to High", value: "price_asc" },
  { label: "Price: High to Low", value: "price_desc" },
];

export default function FilterSidebar({ brands }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function setParam(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (params.get(key) === value) {
      params.delete(key);
    } else {
      params.set(key, value);
      params.delete("page");
    }
    router.push(`/catalog?${params.toString()}`);
  }

  function clearAll() {
    router.push("/catalog");
  }

  const currentStyle = searchParams.get("style");
  const currentBrand = searchParams.get("brand");
  const currentSort = searchParams.get("sort");
  const hasFilters = currentStyle || currentBrand || currentSort;

  return (
    <aside className="w-full lg:w-48 shrink-0">
      <div className="sticky top-20 space-y-7">
        <div className="flex items-center justify-between">
          <p className="text-[10px] uppercase tracking-[0.25em] text-drift-400">Refine</p>
          {hasFilters && (
            <button onClick={clearAll} className="text-[10px] uppercase tracking-wide text-terra-400 hover:text-terra-600 transition-colors">
              Clear
            </button>
          )}
        </div>

        {/* Style */}
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-drift-400 mb-2.5">Style</p>
          <div className="space-y-0.5">
            {STYLES.map(({ label, value }) => (
              <button
                key={value}
                onClick={() => setParam("style", value)}
                className={`block w-full text-left text-sm py-1.5 transition-colors ${
                  currentStyle === value
                    ? "text-terra-500 font-medium"
                    : "text-drift-600 hover:text-terra-500"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Brand */}
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-drift-400 mb-2.5">Brand</p>
          <div className="space-y-0.5 max-h-56 overflow-y-auto">
            {brands.map((b) => (
              <button
                key={b.brand_slug}
                onClick={() => setParam("brand", b.brand_slug)}
                className={`block w-full text-left text-sm py-1.5 transition-colors ${
                  currentBrand === b.brand_slug
                    ? "text-terra-500 font-medium"
                    : "text-drift-600 hover:text-terra-500"
                }`}
              >
                {b.brand}
              </button>
            ))}
          </div>
        </div>

        {/* Sort */}
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-drift-400 mb-2.5">Sort</p>
          <div className="space-y-0.5">
            {SORT_OPTIONS.map(({ label, value }) => (
              <button
                key={value}
                onClick={() => setParam("sort", value)}
                className={`block w-full text-left text-sm py-1.5 transition-colors ${
                  currentSort === value
                    ? "text-terra-500 font-medium"
                    : "text-drift-600 hover:text-terra-500"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
