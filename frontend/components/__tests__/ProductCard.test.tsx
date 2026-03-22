import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import ProductCard from "../ProductCard";
import type { Product } from "@/types/product";

const mockProduct: Product = {
  id: "frankies-abc",
  brand: "Frankies Bikinis",
  brand_slug: "frankies-bikinis",
  name: "The Malibu Top",
  price: 98,
  sale_price: null,
  image_url: "https://example.com/img.jpg",
  affiliate_url: "https://example.com/track/123",
  style: "top",
  colors: ["black"],
  sizes: ["XS", "S", "M"],
  in_stock: true,
  updated_at: "2026-03-21T00:00:00",
};

test("renders brand name and product name", () => {
  render(<ProductCard product={mockProduct} />);
  expect(screen.getByText("Frankies Bikinis")).toBeInTheDocument();
  expect(screen.getByText("The Malibu Top")).toBeInTheDocument();
});

test("renders price", () => {
  render(<ProductCard product={mockProduct} />);
  expect(screen.getByText("$98")).toBeInTheDocument();
});

test("renders sale price when present", () => {
  render(<ProductCard product={{ ...mockProduct, sale_price: 69 }} />);
  expect(screen.getByText("$69")).toBeInTheDocument();
  expect(screen.getByText("$98")).toBeInTheDocument();
});

test("links point to product detail page", () => {
  render(<ProductCard product={mockProduct} />);
  const links = screen.getAllByRole("link");
  expect(links.some(l => l.getAttribute("href") === "/product/frankies-abc")).toBe(true);
});
