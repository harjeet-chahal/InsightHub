'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    Files,
    Lightbulb,
    ClipboardList,
    Download,
    Settings
} from 'lucide-react';

const navItems = [
    { name: 'Dashboard', href: 'dashboard', icon: LayoutDashboard },
    { name: 'Sources', href: 'sources', icon: Files },
    { name: 'Themes', href: 'themes', icon: Lightbulb },
    { name: 'Scorecards', href: 'scorecards', icon: ClipboardList },
    { name: 'Exports', href: 'exports', icon: Download },
];

export function Sidebar({ workspaceId }: { workspaceId: string }) {
    const pathname = usePathname();

    return (
        <div className="flex h-full w-64 flex-col border-r bg-gray-50/40">
            <div className="flex h-14 items-center border-b px-6 font-semibold">
                InsightHub
            </div>
            <div className="flex-1 overflow-auto py-2">
                <nav className="grid items-start px-4 text-sm font-medium">
                    {navItems.map((item) => {
                        const href = \`/workspaces/\${workspaceId}/\${item.href}\`;
                    const isActive = pathname.includes(item.href);
                    return (
                    <Link
                        key={item.href}
                        href={href}
                        className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-gray-900",
                            isActive ? "bg-gray-100 text-gray-900" : "text-gray-500"
                        )}
                    >
                        <item.icon className="h-4 w-4" />
                        {item.name}
                    </Link>
                    );
          })}
                </nav>
            </div>
        </div>
    );
}
