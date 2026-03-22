import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "./components/Navigation";

export const metadata: Metadata = {
  title: "Rescoring Observatory",
  description:
    "Enterprise ML observability for shallow fusion speech correction. Monitor, audit, and validate autonomous transcription decisions.",
  openGraph: {
    title: "Rescoring Observatory",
    description:
      "Real-time observability for autonomous speech correction decisions.",
    type: "website",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        <main>{children}</main>
        <footer className="site-footer">
          &copy; 2026 Rescoring Observatory. All rights reserved.
        </footer>
      </body>
    </html>
  );
}
