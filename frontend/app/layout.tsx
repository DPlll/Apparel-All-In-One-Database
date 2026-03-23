import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Cormorant_Garamond } from "next/font/google";
import "./globals.css";
import NavHeader from "@/components/NavHeader";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-cormorant",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Swim&Co — Discover Women's Swimwear",
  description: "Browse and shop top women's swimwear brands in one place.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${cormorant.variable}`}>
      <body>
        <NavHeader />
        <main>{children}</main>
        <footer className="mt-20 py-10 border-t border-vintage-200 text-center text-xs text-drift-400 tracking-widest uppercase">
          © 2026 Swim&amp;Co &nbsp;·&nbsp; All links are affiliate links.
        </footer>
      </body>
    </html>
  );
}
