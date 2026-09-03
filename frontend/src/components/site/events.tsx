"use client";

import Image from "next/image";

const EVENTS = [
  {
    date: "August 16, 2026",
    title: "Community Planting Day: Coastal Restoration",
    body: "Restoring native mangrove belts to protect against coastal erosion.",
    cta: "Register Now",
    image: "https://images.unsplash.com/photo-1516214104703-d870798883c5?w=1400&q=80&auto=format&fit=crop",
    alt: "Volunteers carrying out coastal tree planting",
  },
  {
    date: "July 23, 2026",
    title: "Workshop: Sustainable Seedling Care",
    body: "Learning essential techniques for nursery care and sapling maintenance.",
    cta: "Reserve Your Spot",
    image: "https://images.unsplash.com/photo-1476231682828-37e571bc172f?w=1400&q=80&auto=format&fit=crop",
    alt: "Hands nurturing a small green plant seedling",
  },
];

export function Events() {
  return (
    <section id="events" className="bg-[#F4F5F2] px-6 py-20 sm:py-28">
      <div className="mx-auto max-w-5xl">
        {/* Category Label */}
        <p className="text-xs font-semibold tracking-widest text-gray-500 uppercase">
          Latest Events
        </p>

        {/* Section Header with Heading + Action Button */}
        <div className="mt-3 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <h2 className="font-serif text-3xl font-normal tracking-tight text-gray-900 sm:text-4xl md:text-5xl">
              Grow with Rooted.
            </h2>
            <p className="mt-2 text-xs text-gray-600 sm:text-sm">
              Join our upcoming planting days and workshops. Be part of the change in your local community.
            </p>
          </div>

          <a
            href="#events"
            className="self-start rounded-full bg-[#121412] px-5 py-2.5 text-xs font-semibold text-white shadow-sm transition-all hover:bg-black sm:self-auto"
          >
            Explore All Events
          </a>
        </div>

        {/* 2 Featured Event Cards */}
        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {EVENTS.map((event) => (
            <div
              key={event.title}
              className="group relative flex h-[380px] flex-col justify-between overflow-hidden rounded-2xl p-6 sm:p-8 shadow-md"
            >
              {/* Card Background Image */}
              <Image
                src={event.image}
                alt={event.alt}
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-105"
                sizes="(min-width: 768px) 50vw, 100vw"
              />

              {/* Dark Gradient Overlay for text contrast */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/40 to-black/20" />

              {/* Date Tag Pill */}
              <div className="relative z-10 self-start">
                <span className="rounded-full bg-white/90 px-3.5 py-1 text-[11px] font-medium text-gray-900 shadow-2xs backdrop-blur-xs">
                  {event.date}
                </span>
              </div>

              {/* Bottom Content Area */}
              <div className="relative z-10">
                <h3 className="font-serif text-xl font-medium text-white sm:text-2xl">
                  {event.title}
                </h3>
                <p className="mt-2 max-w-md text-xs text-gray-300 sm:text-sm">
                  {event.body}
                </p>

                <div className="mt-5">
                  <button
                    type="button"
                    className="rounded-full bg-white px-5 py-2 text-xs font-semibold text-gray-900 shadow-sm transition-all hover:bg-gray-100 hover:shadow-md"
                  >
                    {event.cta}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
