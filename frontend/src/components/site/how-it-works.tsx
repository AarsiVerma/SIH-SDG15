const STEPS = [
  {
    n: "01",
    title: "Detect & track",
    body: "Camera footage is scanned for person, vehicle, animal, fire and smoke. Each object is followed over time — never judged from a single frame.",
  },
  {
    n: "02",
    title: "Score & explain",
    body: "Zone, time of day and ranger proximity feed a transparent risk score. Every factor is listed, including the ones that lower it.",
    example: "restricted zone +25 · nighttime +10 · ranger nearby −40 → 50 / 100",
  },
  {
    n: "03",
    title: "Alert & respond",
    body: "Rangers receive an operational case, not a verdict. They verify, they act, and the outcome is recorded — never assumed.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-paper px-6 py-24 sm:py-32">
      <div className="mx-auto max-w-5xl">
        <p className="text-[0.9rem] text-ink/55">How it works</p>
        <h2 className="mt-3 max-w-[30ch] text-balance font-serif text-[clamp(1.7rem,3.4vw,2.3rem)] leading-[1.25] font-medium text-ink">
          Risk prediction, alert, response — in that order, every time.
        </h2>

        <div className="mt-16 grid gap-10 sm:grid-cols-3 sm:gap-8">
          {STEPS.map((step) => (
            <div key={step.n} className="border-t border-line-light pt-6">
              <p className="font-serif text-[0.95rem] text-ochre">{step.n}</p>
              <h3 className="mt-3 font-serif text-[1.15rem] font-medium text-ink">
                {step.title}
              </h3>
              <p className="mt-3 max-w-[38ch] text-[0.92rem] leading-relaxed text-ink/65">
                {step.body}
              </p>
              {step.example && (
                <p className="mt-4 font-mono text-[0.72rem] leading-relaxed text-ink/45">
                  {step.example}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
