import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

/**
 * Four quiet variants — no glow, no shadow. "accent" (ochre) is reserved
 * for the sparing CTA moment; everything else is charcoal, paper, or a
 * plain border.
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full px-6 py-3 text-[0.92rem] font-medium transition-colors duration-200 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        dark: "bg-ink text-paper hover:bg-forest",
        "outline-dark": "border border-ink/30 text-ink hover:border-ink",
        "outline-light": "border border-birch/40 text-birch hover:border-birch",
        accent: "bg-ochre text-forest hover:bg-ochre-soft",
      },
    },
    defaultVariants: { variant: "dark" },
  },
);

export interface ButtonLinkProps
  extends React.AnchorHTMLAttributes<HTMLAnchorElement>,
    VariantProps<typeof buttonVariants> {}

export function ButtonLink({ className, variant, ...props }: ButtonLinkProps) {
  return (
    <a className={cn(buttonVariants({ variant }), className)} {...props} />
  );
}

export { buttonVariants };
