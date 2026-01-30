import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function LandingPage() {
  return (
    <div className="flex h-screen flex-col bg-white">
      <header className="flex h-16 items-center justify-between border-b px-8">
        <div className="text-xl font-bold">InsightHub</div>
        <nav className="flex gap-4">
          <Link href="/workspaces">
            <Button>Go to Console</Button>
          </Link>
        </nav>
      </header>
      <main className="flex flex-1 flex-col items-center justify-center gap-6 px-4 text-center">
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl">
          Turn Chaos into <span className="text-blue-600">Insights</span>
        </h1>
        <p className="max-w-2xl text-lg text-gray-500">
          Centralize your market research data, extract themes with AI, calculate brand scorecards, and export professional reports in minutes.
        </p>
        <div className="flex gap-4">
          <Link href="/workspaces">
            <Button size="lg" className="h-12 px-8 text-lg">
              Get Started
            </Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
