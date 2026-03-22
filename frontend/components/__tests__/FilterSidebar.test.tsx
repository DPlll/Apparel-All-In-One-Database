import { render, screen, fireEvent } from "@testing-library/react";
import FilterSidebar from "../FilterSidebar";

const mockPush = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => new URLSearchParams(""),
}));

beforeEach(() => { mockPush.mockReset(); });

test("renders style filter options", () => {
  render(<FilterSidebar brands={[{ brand: "Frankies", brand_slug: "frankies-bikinis", product_count: 5 }]} />);
  expect(screen.getByText("Tops")).toBeInTheDocument();
  expect(screen.getByText("Bottoms")).toBeInTheDocument();
  expect(screen.getByText("Sets")).toBeInTheDocument();
  expect(screen.getByText("One-Pieces")).toBeInTheDocument();
});

test("renders brand filter option", () => {
  render(<FilterSidebar brands={[{ brand: "Frankies", brand_slug: "frankies-bikinis", product_count: 5 }]} />);
  expect(screen.getByText("Frankies")).toBeInTheDocument();
});

test("style filter calls router.push with style param on click", () => {
  render(<FilterSidebar brands={[]} />);
  fireEvent.click(screen.getByText("Tops"));
  expect(mockPush).toHaveBeenCalledWith(expect.stringContaining("style=top"));
});
