"use client";

const CARDS = [
  {
    title: "Restoring Biodiversity",
    body: "We prioritize native trees to support local wildlife and stabilize the soil.",
    activeDots: [true, true, false],
  },
  {
    title: "Empowering Action",
    body: "We provide the tools and knowledge for anyone to make a tangible impact.",
    activeDots: [true, true, false],
  },
  {
    title: "Building Community",
    body: "We believe that caring for the earth is best done together.",
    activeDots: [true, true, true],
  },
];

export function About() {
  return (
    <section id="about" className="relative overflow-hidden bg-[#0B100C] px-6 py-24 text-white sm:py-32">
      {/* Background Watermark SVG Tree Pattern */}
      <div className="pointer-events-none absolute right-[-5%] top-1/2 -translate-y-1/2 opacity-[0.04]">
        <svg
          width="600"
          height="600"
          viewBox="0 0 200 200"
          fill="none"
          stroke="currentColor"
          className="text-white"
        >
          <circle cx="100" cy="100" r="20" strokeWidth="0.5" />
          <circle cx="100" cy="100" r="35" strokeWidth="0.5" />
          <circle cx="100" cy="100" r="50" strokeWidth="0.5" />
          <circle cx="100" cy="100" r="65" strokeWidth="0.5" />
          <circle cx="100" cy="100" r="80" strokeWidth="0.5" />
          <circle cx="100" cy="100" r="95" strokeWidth="0.5" />
          <path d="M100 5 L100 195 M5 100 L195 100" strokeWidth="0.25" />
        </svg>
      </div>

      <div className="relative z-10 mx-auto max-w-5xl">
        {/* Category Label */}
        <p className="text-xs font-semibold tracking-widest text-gray-400 uppercase">
          About Us
        </p>

        {/* Headline */}
        <h2 className="mt-6 max-w-4xl font-serif text-2xl leading-snug font-normal text-gray-100 sm:text-3xl md:text-4xl">
          We keep our mission simple: Restore. Educate. Sustain. By focusing on
          native species and evidence-based planting methods, we ensure that
          every tree we plant is a step toward a resilient, healthy ecosystem.
        </h2>

        {/* Secondary paragraph */}
        <p className="mt-6 max-w-4xl text-sm leading-relaxed text-gray-400 sm:text-base">
          At <span className="font-semibold text-gray-200">Rooted</span>, we
          believe that true restoration starts with collective action. Founded by
          a group of nature enthusiasts, our community has grown into a movement
          that empowers individuals to reclaim their local landscapes. We aren&apos;t
          just planting trees; we are actively restoring biodiversity, cleaning
          our air, and teaching the next generation the value of sustainable
          stewardship.
        </p>

        {/* Subtle Horizontal Line */}
        <div className="my-14 border-t border-gray-800/80" />

        {/* Feature Cards Grid */}
        <div className="grid gap-6 sm:grid-cols-3">
          {CARDS.map((card) => (
            <div
              key={card.title}
              className="flex flex-col justify-between rounded-xl border border-white/10 bg-white/[0.04] p-6 transition-all hover:bg-white/[0.07]"
            >
              <div>
                <h3 className="font-sans text-base font-semibold text-gray-100">
                  {card.title}
                </h3>
                <p className="mt-3 text-xs leading-relaxed text-gray-400">
                  {card.body}
                </p>
              </div>

              {/* Status Indicator Dots */}
              <div className="mt-6 flex items-center gap-1.5">
                {card.activeDots.map((isActive, idx) => (
                  <span
                    key={idx}
                    className={`h-2 w-2 rounded-xs ${
                      isActive ? "bg-gray-200" : "bg-gray-700"
                    }`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
