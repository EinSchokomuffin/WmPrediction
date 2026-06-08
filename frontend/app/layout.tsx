import "./globals.css";

import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "WM 2026 Predictor",
  description: "Data-driven FIFA World Cup 2026 prediction app",
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="de">
      <body>
        <main>
          <header className="card" style={{ marginBottom: 16 }}>
            <h1 style={{ marginTop: 0 }}>WM 2026 Predictor</h1>
            <nav style={{ display: "flex", gap: 12 }}>
              <Link href="/">Dashboard</Link>
              <Link href="/setup">Setup</Link>
              <Link href="/groups">Gruppen</Link>
              <Link href="/bracket">Bracket</Link>
              <Link href="/simulation">Simulation</Link>
            </nav>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
