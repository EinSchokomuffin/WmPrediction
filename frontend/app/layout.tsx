import "./globals.css";

import type { Metadata } from "next";

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
          <header className="card hero-card" style={{ marginBottom: 16 }}>
            <h1 style={{ marginTop: 0 }}>WM 2026 Predictor</h1>
            <p style={{ marginBottom: 0 }}>Wähle einfach zwei Teams aus und lass das erwartete Ergebnis berechnen.</p>
          </header>
          {children}
        </main>
      </body>
    </html>
  );
}
