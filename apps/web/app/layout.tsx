import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LevelUpOS",
  description: "Your AI-powered gamified personal operating system"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
