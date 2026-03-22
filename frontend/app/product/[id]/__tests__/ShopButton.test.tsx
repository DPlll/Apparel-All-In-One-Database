import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ShopButton from "../ShopButton";

const mockWindowOpen = jest.fn();
const mockWindowClose = jest.fn();

function makeMockWin(url = "") {
  return { location: { href: url }, close: mockWindowClose };
}

global.fetch = jest.fn();

beforeEach(() => {
  mockWindowOpen.mockReset();
  mockWindowClose.mockReset();
  (global.fetch as jest.Mock).mockReset();
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: true,
    json: async () => ({ affiliate_url: "https://brand.com/product/123" }),
  });
  // Default: popup allowed
  mockWindowOpen.mockReturnValue(makeMockWin());
  Object.defineProperty(window, "open", { value: mockWindowOpen, writable: true, configurable: true });
});

test("renders button with brand name", () => {
  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  expect(screen.getByRole("button", { name: /shop at frankies bikinis/i })).toBeInTheDocument();
});

test("opens blank window synchronously, then sets location to affiliate URL", async () => {
  const mockWin = makeMockWin();
  mockWindowOpen.mockReturnValue(mockWin);

  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  fireEvent.click(screen.getByRole("button"));

  // window.open("", "_blank") must be called synchronously (before any await)
  expect(mockWindowOpen).toHaveBeenCalledWith("", "_blank");

  await waitFor(() => {
    expect(mockWin.location.href).toBe("https://brand.com/product/123");
  });

  const fetchCall = (global.fetch as jest.Mock).mock.calls[0];
  expect(fetchCall[0]).toContain("/click/frankies-abc");
  expect(fetchCall[1]?.method).toBe("POST");
});

test("button is disabled and shows 'Opening…' while loading", async () => {
  // Hold the fetch promise so we can inspect loading state
  let resolveFetch!: (v: unknown) => void;
  (global.fetch as jest.Mock).mockReturnValue(
    new Promise((res) => { resolveFetch = res; })
  );

  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  const btn = screen.getByRole("button");
  fireEvent.click(btn);

  expect(btn).toBeDisabled();
  expect(btn).toHaveTextContent("Opening…");

  // Resolve the fetch to finish loading
  resolveFetch({
    ok: true,
    json: async () => ({ affiliate_url: "https://brand.com/product/123" }),
  });
  await waitFor(() => expect(btn).not.toBeDisabled());
});

test("shows error message and re-enables button when postClick throws", async () => {
  (global.fetch as jest.Mock).mockRejectedValue(new Error("network error"));

  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  const btn = screen.getByRole("button");
  fireEvent.click(btn);

  await waitFor(() => {
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  expect(btn).not.toBeDisabled();
  expect(btn).toHaveTextContent(/shop at frankies bikinis/i);
});

test("closes the blank window if postClick throws", async () => {
  const mockWin = { location: { href: "" }, close: mockWindowClose };
  mockWindowOpen.mockReturnValue(mockWin);
  (global.fetch as jest.Mock).mockRejectedValue(new Error("network error"));

  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  fireEvent.click(screen.getByRole("button"));

  await waitFor(() => {
    expect(mockWindowClose).toHaveBeenCalled();
  });
});

test("falls back to window.location when popup is blocked (win is null)", async () => {
  mockWindowOpen.mockReturnValue(null);

  // jsdom's window.location is non-configurable by default; delete then redefine to allow spying.
  const locationHrefSetter = jest.fn();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  delete (window as any).location;
  Object.defineProperty(window, "location", {
    value: { href: "", assign: jest.fn() },
    writable: true,
    configurable: true,
  });
  Object.defineProperty(window.location, "href", {
    set: locationHrefSetter,
    get: () => "",
    configurable: true,
  });

  render(<ShopButton productId="frankies-abc" brandName="Frankies Bikinis" />);
  fireEvent.click(screen.getByRole("button"));

  await waitFor(() => {
    expect(locationHrefSetter).toHaveBeenCalledWith("https://brand.com/product/123");
  });
});
