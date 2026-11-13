import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Zyro HR Assistant | Zyro Dynamics Pvt. Ltd.',
  description: 'AI-Powered HR Help Desk & RAG Policy Search for Zyro Dynamics Pvt. Ltd.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}

