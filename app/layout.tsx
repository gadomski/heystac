import { Metadata } from "next";
import { Inter } from "next/font/google";
import Header from "./header";
import Provider from "./provider";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "heystac",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html className={inter.className} suppressHydrationWarning>
      <head></head>
      <body>
        <Provider>
          <Header></Header>
          <main>{children}</main>
        </Provider>
      </body>
    </html>
  );
}
