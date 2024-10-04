import { RootProvider } from "fumadocs-ui/provider";
import localFont from "next/font/local";
import type { ReactNode } from "react";
import "./global.css";

const pretendard = localFont({
  src: "../assets/PretendardVariable.woff2",
  display: "swap",
  weight: "45 920",
});

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko" className={pretendard.className} suppressHydrationWarning>
      <body>
        <RootProvider
          search={{
            enabled: false, // TODO: enable search after fumadocs supports it
          }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  );
}
