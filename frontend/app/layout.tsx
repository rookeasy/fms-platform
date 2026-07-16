import type { Metadata } from "next";
import type { ReactNode } from "react";

import { fuzionBrand } from "@/lib/brand";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: fuzionBrand.pageTitle,
    template: `%s | ${fuzionBrand.productName}`
  },
  description: `${fuzionBrand.product} - ${fuzionBrand.missionControlSubtitle} - ${fuzionBrand.tagline}`,
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
