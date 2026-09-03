import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";

const LINKS = [
  { label: "How it works", href: "#how-it-works" },
  { label: "Scenarios", href: "#scenarios" },
];

export function Navbar() {
  return (
    <header className="relative z-20 border-b border-line-light bg-paper">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link
          href="/"
          className="font-serif text-[1.15rem] tracking-tight text-ink"
        >
          Vanraksha
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[0.9rem] text-ink/70 transition-colors duration-200 hover:text-ink"
            >
              {link.label}
            </a>
          ))}
        </div>

        <Link
          href="/command"
          className={buttonVariants({ variant: "outline-dark" }) + " px-5 py-2 text-[0.85rem]"}
        >
          Command Centre
        </Link>
      </nav>
    </header>
  );
}
