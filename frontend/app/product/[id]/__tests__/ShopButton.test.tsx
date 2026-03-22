import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ShopButton from "../ShopButton";

const mockOpen = jest.fn();
Object.defineProperty(window, "open", { value: mockOpen, writable: true });

global.fetch = jest.fn();

beforeEach(() => {
  mockOpen.mockReset();
  (global.fetch as jest.Mock).mockReset();
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: async () => ({ affiliate_url: "https://brand.com/product/123" }),
  });
});

test("renders button with brand name", () => {
  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  expect(screen.getByRole("button", { name: /shop at frankies bikinis/i })).toBeInTheDocument();
});

test("calls POST /click/{id} and opens affiliate URL on click", async () => {
  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  fireEvent.click(screen.getByRole("button"));

  await waitFor(() => {
    expect(window.open).toHaveBeenCalledWith("https://brand.com/product/123", "_blank");
  });

  const fetchCall = (global.fetch as jest.Mock).mock.calls[0];
  expect(fetchCall[0]).toContain("/click/frankies-abc");
  expect(fetchCall[1]?.method).toBe("POST");
});
