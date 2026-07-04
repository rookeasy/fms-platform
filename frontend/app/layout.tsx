import type { Metadata } from "next";
import type { ReactNode } from "react";
import { fuzionBrand } from "@/lib/brand";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "FPP | Fuzion Protection Platform",
    template: `%s | ${fuzionBrand.shortName}`
  },
  description: `${fuzionBrand.product} - ${fuzionBrand.tagline}`,
  icons: {
    icon: "/icon.svg"
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

