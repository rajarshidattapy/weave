import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { ClerkProvider } from '@clerk/nextjs'
import { dark } from '@clerk/themes'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'Weave',
  description: 'Weave the Web with AI',
  generator: 'Weave',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans antialiased bg-background text-foreground">
        <ClerkProvider
          appearance={{
            baseTheme: dark,
            variables: {
              colorPrimary: '#3b82f6',
              colorBackground: '#000000',
              colorInputBackground: '#111111',
              colorInputText: '#ffffff',
            },
            elements: {
              card: 'bg-black/60 backdrop-blur-2xl border border-white/10 shadow-2xl rounded-2xl',
              socialButtonsBlockButton: 'border border-white/10 hover:bg-white/5 bg-black text-white',
              formFieldInput: 'bg-black border border-white/20 focus:border-blue-500 rounded-lg text-white placeholder:text-white/30',
              footerActionLink: 'text-blue-400 hover:text-blue-300',
            }
          }}
        >
          {children}
          {process.env.NODE_ENV === 'production' && <Analytics />}
        </ClerkProvider>
      </body>
    </html>
  )
}
