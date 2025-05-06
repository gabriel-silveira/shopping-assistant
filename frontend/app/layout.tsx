import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "./components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Assistente Virtual CSN",
  description: "Assistente virtual para consulta de produtos CSN",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <Header />
          {/* Espaçador para compensar o header fixo */}
          <div className="h-[100px]"></div>
          {/* Container principal com altura total e rolagem */}
          <main className="flex-1 bg-gray-200 fixed top-[100px] left-0 right-0 bottom-0 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
