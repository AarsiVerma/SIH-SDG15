"use client";

import Image from "next/image";

export function Testimonial() {
  return (
    <section className="relative bg-[#F4F5F2] px-6 py-20">
      <div className="mx-auto max-w-4xl">
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-6">
          {/* Avatar Image */}
          <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-md border border-gray-200 shadow-xs">
            <Image
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80&auto=format&fit=crop"
              alt="Jack Robinson - Founder of Rooted"
              fill
              className="object-cover"
              sizes="56px"
            />
          </div>

          {/* Quote & Author Info */}
          <div>
            <blockquote className="font-sans text-sm leading-relaxed text-gray-800 sm:text-base md:text-lg">
              &ldquo;To create a world where every community actively participates
              in the restoration and protection of their natural landscapes,
              creating a greener, more breathable planet for generations to
              come.&rdquo;
            </blockquote>
            <p className="mt-2 text-xs font-medium text-gray-500">
              Jack Robinson &bull; Founder of Rooted
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
