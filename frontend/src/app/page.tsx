import { Navbar } from "@/components/site/navbar";
import { Hero } from "@/components/site/hero";
import { About } from "@/components/site/about";
import { Testimonial } from "@/components/site/testimonial";
import { Stats } from "@/components/site/stats";
import { Events } from "@/components/site/events";
import { CTA } from "@/components/site/cta";
import { Footer } from "@/components/site/footer";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-[#F4F5F2] text-gray-900 overflow-x-hidden">
      <Navbar />
      <Hero />
      <About />
      <Testimonial />
      <Stats />
      <Events />
      <CTA />
      <Footer />
    </main>
  );
}
