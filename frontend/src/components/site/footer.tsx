"use client";

import Link from "next/link";
import { TreePine } from "lucide-react";

const FOOTER_NAV = [
  {
    title: "Menu",
    links: [
      { label: "Home", href: "#" },
      { label: "About Us", href: "#about" },
      { label: "Our Mission", href: "#mission" },
      { label: "Our Impact", href: "#impact" },
    ],
  },
  {
    title: "Resource",
    links: [
      { label: "Blog & Article", href: "#" },
      { label: "Workshop", href: "#events" },
      { label: "Community", href: "#about" },
    ],
  },
  {
    title: "Other",
    links: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Cookie Setting", href: "#" },
    ],
  },
];

const SOCIAL_LINKS = ["Instagram", "Twitter", "Threads", "LinkedIn"];

export function Footer() {
  return (
    <footer id="footer" className="bg-[#F4F5F2] px-4 pb-12 pt-6 sm:px-8">
      <div className="mx-auto max-w-5xl rounded-3xl border border-white/10 bg-[#0B100C] p-8 text-white shadow-2xl sm:p-12">
        <div className="grid gap-12 lg:grid-cols-12">
          {/* Left Column: Email Subscribe & Info */}
          <div className="flex flex-col justify-between lg:col-span-6">
            <div>
              <h3 className="font-sans text-xl font-medium tracking-tight text-white sm:text-2xl">
                Stay connected to the earth.
              </h3>
              <p className="mt-2 max-w-sm text-xs leading-relaxed text-gray-400 sm:text-sm">
                Receive updates on our planting progress and be the first to know about upcoming events.
              </p>

              {/* Email Form */}
              <form
                onSubmit={(e) => e.preventDefault()}
                className="mt-6 flex max-w-md items-center rounded-full border border-white/20 bg-white/10 p-1.5 backdrop-blur-xs"
              >
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="w-full bg-transparent px-4 text-xs text-white placeholder-gray-400 focus:outline-none"
                  required
                />
                <button
                  type="submit"
                  className="shrink-0 rounded-full bg-white px-5 py-2 text-xs font-semibold text-gray-900 transition-all hover:bg-gray-100"
                >
                  Subscribe
                </button>
              </form>
            </div>

            {/* Logo at Bottom Left */}
            <div className="mt-10 flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10">
                <TreePine className="h-3.5 w-3.5 text-white stroke-[1.75]" />
              </div>
              <span className="font-serif text-sm font-medium text-white tracking-tight">
                Rooted
              </span>
            </div>
          </div>

          {/* Right Column: Navigation Links */}
          <div className="grid grid-cols-3 gap-6 lg:col-span-6">
            {FOOTER_NAV.map((column) => (
              <div key={column.title}>
                <h4 className="text-xs font-semibold tracking-wider text-gray-400 uppercase">
                  {column.title}
                </h4>
                <ul className="mt-4 space-y-2.5">
                  {column.links.map((link) => (
                    <li key={link.label}>
                      <Link
                        href={link.href}
                        className="text-xs text-gray-300 transition-colors hover:text-white"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Social Links Bar */}
        <div className="mt-12 border-t border-white/10 pt-6 flex flex-wrap items-center justify-between text-[11px] text-gray-400">
          <p>&copy; {new Date().getFullYear()} Rooted. All rights reserved.</p>
          <div className="flex items-center gap-4">
            {SOCIAL_LINKS.map((social) => (
              <a
                key={social}
                href="#"
                className="transition-colors hover:text-white"
              >
                {social}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
