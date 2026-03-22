import type { Product, Brand, ProductsResponse, SearchResponse, ProductFilters } from "@/types/product";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}

export function fetchProducts(filters: ProductFilters = {}): Promise<ProductsResponse> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return apiFetch<ProductsResponse>(`/products${qs ? `?${qs}` : ""}`);
}

export function fetchProduct(id: string): Promise<Product> {
  return apiFetch<Product>(`/products/${encodeURIComponent(id)}`);
}

export function fetchBrands(): Promise<Brand[]> {
  return apiFetch<Brand[]>("/brands");
}

export function searchProducts(q: string): Promise<SearchResponse> {
  return apiFetch<SearchResponse>(`/search?q=${encodeURIComponent(q)}`);
}

export function postClick(id: string): Promise<{ affiliate_url: string }> {
  return apiFetch<{ affiliate_url: string }>(`/click/${encodeURIComponent(id)}`, {
    method: "POST",
  });
}
