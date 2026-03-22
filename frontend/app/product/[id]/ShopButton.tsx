"use client";

import { useState } from "react";
import { postClick } from "@/lib/api";

interface Props {
  productId: string;
  brandName: string;
}

export default function ShopButton({ productId, brandName }: Props) {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    try {
      const { affiliate_url } = await postClick(productId);
      window.open(affiliate_url, "_blank");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="w-full py-3.5 border border-stone-900 text-stone-900 text-xs tracking-[0.2em] uppercase hover:bg-stone-900 hover:text-white transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading ? "Opening…" : `Shop at ${brandName}`}
    </button>
  );
}
