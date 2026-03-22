export interface Product {
  id: string;
  brand: string;
  brand_slug: string;
  name: string;
  price: number;
  sale_price: number | null;
  image_url: string;
  affiliate_url: string;
  style: "top" | "bottom" | "set" | "one-piece";
  colors: string[];
  sizes: string[];
  in_stock: boolean;
  updated_at: string;
}

export interface Brand {
  brand: string;
  brand_slug: string;
  product_count: number;
}

export interface ProductsResponse {
  items: Product[];
  page: number;
  per_page: number;
  total: number;
}

export interface SearchResponse {
  items: Product[];
}

export interface ProductFilters {
  brand?: string;
  style?: string;
  color?: string;
  size?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  sort?: "price_asc" | "price_desc" | "newest";
  page?: number;
  q?: string;
}
