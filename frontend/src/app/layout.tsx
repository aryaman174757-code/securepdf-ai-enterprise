import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SecurePDF AI Enterprise v3.0 | Zero-Trust AI Document Intelligence",
  description: "Enterprise Zero-Trust AI Document Intelligence, Cryptography, OCR, and Workflow Automation Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const savedTheme = localStorage.getItem('spdf_theme') || 'light';
                if (savedTheme === 'dark') {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className={`${inter.className} bg-background text-gray-900 dark:text-gray-100 min-h-screen flex flex-col antialiased transition-colors duration-200`}>
        {/* Ambient Glows */}
        <div className="fixed top-0 left-1/4 -z-10 h-96 w-96 rounded-full bg-blue-400/10 dark:bg-primary/10 blur-[120px] pointer-events-none" />
        <div className="fixed bottom-0 right-1/4 -z-10 h-96 w-96 rounded-full bg-sky-300/15 dark:bg-accent/10 blur-[120px] pointer-events-none" />

        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
