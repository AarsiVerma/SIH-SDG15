"use client";

const STATS = [
  { value: "50,000+", label: "Native Trees Planted" },
  { value: "120+", label: "Hectares Restored" },
  { value: "2,500+", label: "Active Stewards" },
  { value: "450+", label: "Community Events" },
];

export function Stats() {
  return (
    <section id="impact" className="relative bg-[#F4F5F2] px-6 py-20 sm:py-28">
      <div className="mx-auto max-w-5xl text-center">
        {/* Label */}
        <p className="text-xs font-semibold tracking-widest text-gray-500 uppercase">
          Our Impact
        </p>

        {/* Heading */}
        <h2 className="mt-3 font-serif text-3xl font-normal tracking-tight text-gray-900 sm:text-4xl md:text-5xl">
          Measurable change, organic growth.
        </h2>

        {/* Subtitle */}
        <p className="mt-3 text-xs text-gray-600 sm:text-sm md:text-base">
          Our progress is a testament to the collective power of passionate individuals.
        </p>

        {/* 4-Stat Grid */}
        <div className="mt-16 grid grid-cols-2 gap-8 sm:grid-cols-4">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="font-serif text-3xl font-normal tracking-tight text-gray-900 sm:text-4xl md:text-5xl">
                {stat.value}
              </p>
              <p className="mt-2 text-xs font-medium text-gray-600 sm:text-sm">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
