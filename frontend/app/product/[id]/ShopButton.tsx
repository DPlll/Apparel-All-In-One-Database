"use client";

import { useState } from "react";
import { postClick } from "@/lib/api";

interface Props {
  productId: string;
  brandName: string;
}

export default function ShopButton({ productId, brandName }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  async function handleClick() {
    setLoading(true);
    setError(false);

    // Open the window synchronously during the user gesture to avoid popup blockers.
    const win = window.open("", "_blank");

    try {
      const { affiliate_url } = await postClick(productId);
      if (win) {
        win.location.href = affiliate_url;
      } else {
        // Popup was blocked — fall back to same-tab navigation.
        window.location.href = affiliate_url;
      }
    } catch {
      setError(true);
      if (win) {
        win.close();
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full">
      <button
        onClick={handleClick}
        disabled={loading}
        className="w-full py-3.5 bg-terra-500 text-vintage-50 text-xs tracking-[0.2em] uppercase hover:bg-terra-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-sm"
      >
        {loading ? "Opening…" : `Shop at ${brandName}`}
      </button>
      {error && (
        <p className="mt-2 text-xs text-red-600 text-center">
          Something went wrong. Please try again.
        </p>
      )}
    </div>
  );
}
