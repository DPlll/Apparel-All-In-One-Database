import Link from "next/link";

export default function NavHeader() {
  return (
    <header className="sticky top-0 z-50 bg-vintage-50/95 backdrop-blur-sm border-b border-vintage-200">
      {/* Thin terracotta accent bar */}
      <div className="h-0.5 bg-terra-500" />
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="font-serif text-xl tracking-wide text-drift-900 hover:text-terra-500 transition-colors">
          Swim&amp;Co
        </Link>
        <nav className="flex items-center gap-8 text-xs tracking-widest uppercase text-drift-600">
          <Link href="/catalog" className="hover:text-terra-500 transition-colors">Shop All</Link>
          <Link href="/catalog?style=set" className="hover:text-terra-500 transition-colors">Sets</Link>
          <Link href="/catalog?style=one-piece" className="hover:text-terra-500 transition-colors">One-Pieces</Link>
        </nav>
      </div>
    </header>
  );
}
