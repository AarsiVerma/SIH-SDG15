"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { buttonVariants } from "@/components/ui/button";

export function Hero() {
  const reduced = useReducedMotion();

  return (
    <section className="relative flex h-[88vh] min-h-140 items-end overflow-hidden bg-forest">
      <motion.div
        className="absolute inset-0"
        initial={reduced ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 1.06 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
      >
        <Image
          src="https://images.unsplash.com/photo-1425913397330-cf8af2ff40a1?w=2400&q=80&auto=format&fit=crop"
          alt="Early-morning light through a misty pine reserve"
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-forest via-forest/35 to-forest/10" />
      </motion.div>

      <div className="relative z-10 mx-auto w-full max-w-3xl px-6 pb-20 text-center">
        <h1 className="mx-auto max-w-[19ch] text-balance font-serif text-[clamp(2rem,5vw,3.4rem)] leading-[1.18] font-medium text-birch">
          Forest footage, turned into a decision worth trusting.
        </h1>

        <p className="mx-auto mt-5 max-w-[42ch] text-[1.02rem] leading-relaxed text-birch/75">
          Vanraksha AI watches reserve camera feeds and raises verified,
          explainable alerts — never a verdict.
        </p>

        <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link href="/command" className={buttonVariants({ variant: "dark" })}>
            Enter Command Centre
          </Link>
          <a
            href="#how-it-works"
            className={buttonVariants({ variant: "outline-light" })}
          >
            See how it works
          </a>
        </div>
      </div>
    </section>
  );
}
