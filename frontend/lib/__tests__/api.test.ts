import { fetchProducts, fetchBrands, fetchProduct, postClick } from "../api";

global.fetch = jest.fn();

beforeEach(() => {
  (global.fetch as jest.Mock).mockReset();
});

test("fetchProducts constructs correct URL with filters", async () => {
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: async () => ({ items: [], page: 1, per_page: 24, total: 0 }),
  });

  await fetchProducts({ brand: "frankies-bikinis", style: "top", page: 2 });

  const url = (global.fetch as jest.Mock).mock.calls[0][0] as string;
  expect(url).toContain("brand=frankies-bikinis");
  expect(url).toContain("style=top");
  expect(url).toContain("page=2");
});

test("fetchBrands returns brand array", async () => {
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: async () => [{ brand: "Frankies", brand_slug: "frankies", product_count: 5 }],
  });

  const brands = await fetchBrands();
  expect(brands[0].brand_slug).toBe("frankies");
});

test("fetchProduct fetches single product by id", async () => {
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: async () => ({ id: "frankies-abc", brand: "Frankies", name: "Test" }),
  });

  const product = await fetchProduct("frankies-abc");
  expect(product.id).toBe("frankies-abc");
});

test("postClick returns affiliate_url", async () => {
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: async () => ({ affiliate_url: "https://example.com/track/123" }),
  });

  const result = await postClick("frankies-abc");
  expect(result.affiliate_url).toContain("example.com");
});
