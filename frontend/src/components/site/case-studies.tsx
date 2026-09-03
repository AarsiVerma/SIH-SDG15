import Image from "next/image";

const CASES = [
  {
    tag: "Scenario 01 · Night patrol",
    title: "Restricted-zone activity, after dark",
    body: "A person and vehicle enter a buffer zone at night. Risk rises — then falls the moment a verified ranger is confirmed nearby.",
    link: "How the score is built",
    href: "#how-it-works",
    image: "https://images.unsplash.com/photo-1516214104703-d870798883c5?w=1400&q=80&auto=format&fit=crop",
    alt: "Dense forest reserve interior with a footpath",
  },
  {
    tag: "Scenario 05 · Ranger safety",
    title: "SOS to response, in one tap",
    body: "A ranger's distress signal creates a critical incident instantly, location attached, so response can be coordinated without delay.",
    link: "See the response flow",
    href: "/command",
    image: "https://images.unsplash.com/photo-1476231682828-37e571bc172f?w=1400&q=80&auto=format&fit=crop",
    alt: "Aerial view of a forest track cutting through pine canopy",
  },
];

export function CaseStudies() {
  return (
    <section id="scenarios" className="bg-paper px-6 pb-24 sm:pb-32">
      <div className="mx-auto max-w-5xl">
        <p className="text-[0.9rem] text-ink/55">Field scenarios</p>
        <h2 className="mt-3 max-w-[34ch] text-balance font-serif text-[clamp(1.7rem,3.4vw,2.3rem)] leading-[1.25] font-medium text-ink">
          Two of the seven, end to end.
        </h2>

        <div className="mt-14 grid gap-x-10 gap-y-14 sm:grid-cols-2">
          {CASES.map((c) => (
            <article key={c.title}>
              <div className="relative aspect-[4/3] w-full">
                <Image
                  src={c.image}
                  alt={c.alt}
                  fill
                  className="object-cover"
                  sizes="(min-width: 640px) 50vw, 100vw"
                />
              </div>
              <p className="mt-5 text-[0.8rem] text-ink/50">{c.tag}</p>
              <h3 className="mt-1.5 font-serif text-[1.2rem] font-medium text-ink">
                {c.title}
              </h3>
              <p className="mt-2.5 max-w-[46ch] text-[0.92rem] leading-relaxed text-ink/65">
                {c.body}
              </p>
              <a
                href={c.href}
                className="mt-3 inline-block text-[0.88rem] text-ink underline decoration-ink/30 underline-offset-4 transition-colors hover:decoration-ochre hover:text-ochre-soft"
              >
                {c.link} →
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
