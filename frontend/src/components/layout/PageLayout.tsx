import type { ReactNode } from "react";

interface PageLayoutProps {
  children: ReactNode;
  maxWidth?: string;
}

export function PageLayout({
  children,
  maxWidth = "max-w-xl",
}: PageLayoutProps) {
  return (
    <main className={`${maxWidth} mx-auto py-6 px-4`}>{children}</main>
  );
}
