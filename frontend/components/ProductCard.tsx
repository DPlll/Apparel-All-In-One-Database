import Link from "next/link";
import Image from "next/image";
import type { Product } from "@/types/product";

interface Props {
  product: Product;
}

export default function ProductCard({ product }: Props) {
  return (
    <article className="group">
      <Link href={`/product/${product.id}`} className="block">
        <div className="relative aspect-[3/4] bg-vintage-100 overflow-hidden rounded-xl">
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover group-hover:scale-[1.04] transition-transform duration-700 ease-out"
          />
          {product.sale_price != null && (
            <span className="absolute top-2.5 left-2.5 bg-terra-500 text-vintage-50 text-[9px] font-medium px-2.5 py-1 rounded-full tracking-widest uppercase">
              Sale
            </span>
          )}
        </div>
      </Link>

      <div className="mt-3 px-0.5">
        <p className="text-[10px] uppercase tracking-widest text-drift-400 mb-0.5">{product.brand}</p>
        <Link href={`/product/${product.id}`}>
          <h3 className="font-serif text-sm text-drift-900 leading-snug hover:text-terra-500 transition-colors line-clamp-2">
            {product.name}
          </h3>
        </Link>
        <div className="mt-1 flex items-baseline gap-2">
          {product.sale_price != null ? (
            <>
              <span className="text-sm text-terra-500">${product.sale_price}</span>
              <span className="text-xs text-drift-400 line-through">${product.price}</span>
            </>
          ) : (
            <span className="text-sm text-drift-600">${product.price}</span>
          )}
        </div>
      </div>
    </article>
  );
}
