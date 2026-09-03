import CommandShell from "@/components/layout/CommandShell";

export default function CommandLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <CommandShell>{children}</CommandShell>;
}