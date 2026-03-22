import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import HomePage from "../page";

jest.mock("@/lib/api", () => ({
  fetchBrands: jest.fn().mockResolvedValue([
    { brand: "Frankies Bikinis", brand_slug: "frankies-bikinis", product_count: 10 },
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

test("renders hero heading", async () => {
  render(await HomePage());
  expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
});

test("renders Shop All link to /catalog", async () => {
  render(await HomePage());
  const links = screen.getAllByRole("link");
  expect(links.some(l => l.getAttribute("href") === "/catalog")).toBe(true);
});

test("renders brand name in brands strip", async () => {
  render(await HomePage());
  const matches = screen.getAllByText("Frankies Bikinis");
  expect(matches.length).toBeGreaterThan(0);
});
