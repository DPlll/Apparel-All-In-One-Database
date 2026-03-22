import Link from "next/link";

export default function NavHeader() {
  return (
    <header className="sticky top-0 z-50 bg-sand-50/95 backdrop-blur-sm border-b border-sand-200">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="font-serif text-xl tracking-wide text-stone-900 hover:text-rose-500 transition-colors">
          Swim&amp;Co
        </Link>
        <nav className="flex items-center gap-8 text-xs tracking-widest uppercase text-stone-600">
          <Link href="/catalog" className="hover:text-rose-500 transition-colors">Shop All</Link>
          <Link href="/catalog?style=set" className="hover:text-rose-500 transition-colors">Sets</Link>
          <Link href="/catalog?style=one-piece" className="hover:text-rose-500 transition-colors">One-Pieces</Link>
        </nav>
      </div>
    </header>
  );
}
