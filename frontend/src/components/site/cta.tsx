"use client";

export function CTA() {
  return (
    <section id="mission" className="bg-[#F4F5F2] px-6 py-24 sm:py-32">
      <div className="mx-auto max-w-3xl text-center">
        {/* Top Label */}
        <p className="text-xs font-semibold tracking-widest text-gray-500 uppercase">
          Ready to leave your mark?
        </p>

        {/* Heading */}
        <h2 className="mt-4 font-serif text-3xl font-normal leading-tight tracking-tight text-gray-900 sm:text-4xl md:text-5xl">
          Join our mission to restore nature&apos;s balance and secure a sustainable future.
        </h2>

        {/* Subtitle */}
        <p className="mx-auto mt-4 max-w-lg text-xs leading-relaxed text-gray-600 sm:text-sm md:text-base">
          Nature doesn&apos;t wait, and neither should you. Every action counts on our journey toward a greener future.
        </p>

        {/* Buttons */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <a
            href="#about"
            className="rounded-full bg-[#121412] px-6 py-3 text-xs font-medium text-white shadow-md transition-all hover:bg-black sm:text-sm"
          >
            Join Community
          </a>
          <a
            href="#impact"
            className="rounded-full border border-gray-300/90 bg-white/80 px-6 py-3 text-xs font-medium text-gray-800 shadow-2xs backdrop-blur-xs transition-all hover:bg-white sm:text-sm"
          >
            See Our Impact
          </a>
        </div>
      </div>
    </section>
  );
}
