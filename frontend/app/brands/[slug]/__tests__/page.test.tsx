import { render, screen } from "@testing-library/react";

// Must mock notFound before importing the page
const mockNotFound = jest.fn(() => { throw new Error("NEXT_NOT_FOUND"); });
jest.mock("next/navigation", () => ({ notFound: mockNotFound }));

jest.mock("@/lib/api", () => ({
  fetchBrands: jest.fn().mockResolvedValue([
    { brand: "Frankies Bikinis", brand_slug: "frankies-bikinis", product_count: 3 },
  ]),
  fetchProducts: jest.fn().mockResolvedValue({
    items: [
      {
        id: "frankies-abc",
        brand: "Frankies Bikinis",
        brand_slug: "frankies-bikinis",
        name: "The Malibu Top",
        price: 98,
        sale_price: null,
        image_url: "https://example.com/img.jpg",
        affiliate_url: "https://example.com",
        style: "top",
        colors: ["black"],
        sizes: ["S"],
        in_stock: true,
        updated_at: "2026-03-21T00:00:00",
      },
    ],
    page: 1,
    per_page: 24,
    total: 1,
  }),
}));

import BrandPage from "../page";

test("renders brand name in heading", async () => {
  const jsx = await BrandPage({ params: Promise.resolve({ slug: "frankies-bikinis" }) });
  render(jsx);
  expect(screen.getByRole("heading", { name: "Frankies Bikinis" })).toBeInTheDocument();
});

test("calls notFound for unknown brand slug", async () => {
  await expect(
    BrandPage({ params: Promise.resolve({ slug: "unknown-brand" }) })
  ).rejects.toThrow("NEXT_NOT_FOUND");
});
