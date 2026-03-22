import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { fetchProduct } from "@/lib/api";
import ShopButton from "./ShopButton";

export const dynamic = "force-dynamic";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function ProductPage({ params }: PageProps) {
  const { id } = await params;

  let product;
  try {
    product = await fetchProduct(id);
  } catch {
    notFound();
  }

  if (!product) notFound();

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <Link
        href="/catalog"
        className="text-[11px] uppercase tracking-widest text-stone-400 hover:text-rose-500 transition-colors mb-8 inline-block"
      >
        ← All Swimwear
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Image */}
        <div className="relative aspect-[3/4] overflow-hidden bg-sand-100 rounded-sm">
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            priority
            sizes="(max-width: 768px) 100vw, 50vw"
            className="object-cover"
          />
        </div>

        {/* Info */}
        <div className="flex flex-col justify-center space-y-6 py-4">
          <div>
            <Link
              href={`/brands/${product.brand_slug}`}
              className="text-[10px] uppercase tracking-[0.25em] text-stone-400 hover:text-rose-500 transition-colors"
            >
              {product.brand}
            </Link>
            <h1 className="font-serif text-3xl text-stone-900 mt-2 leading-snug">
              {product.name}
            </h1>
          </div>

          {/* Price */}
          <div className="flex items-baseline gap-3">
            {product.sale_price != null ? (
              <>
                <span className="text-2xl text-rose-500">${product.sale_price}</span>
                <span className="text-base text-stone-400 line-through">${product.price}</span>
              </>
            ) : (
              <span className="text-2xl text-stone-800">${product.price}</span>
            )}
          </div>

          {/* Sizes */}
          {product.sizes.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-stone-400 mb-3">Sizes</p>
              <div className="flex flex-wrap gap-2">
                {product.sizes.map((size) => (
                  <span key={size} className="px-3 py-1.5 border border-sand-300 text-xs text-stone-600">
                    {size}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Colors */}
          {product.colors.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-stone-400 mb-3">Colors</p>
              <div className="flex flex-wrap gap-2">
                {product.colors.map((color) => (
                  <span key={color} className="px-3 py-1.5 border border-sand-300 text-xs text-stone-600 capitalize">
                    {color}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* CTA */}
          <div className="pt-2">
            {product.in_stock ? (
              <ShopButton productId={product.id} brandName={product.brand} />
            ) : (
              <p className="text-xs uppercase tracking-widest text-stone-400 text-center py-3">
                Out of stock
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
