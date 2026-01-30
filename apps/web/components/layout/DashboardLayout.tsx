'use client';

import { Sidebar } from './Sidebar';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function DashboardLayout({
    children,
    workspaceId
}: {
    children: React.ReactNode;
    workspaceId: string;
}) {
    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar workspaceId={workspaceId} />
            <div className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-14 items-center gap-4 border-b bg-white px-6">
                    <Link href="/workspaces" className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900">
                        <ArrowLeft className="h-4 w-4" />
                        Back to Workspaces
                    </Link>
                </header>
                <main className="flex-1 overflow-y-auto bg-gray-50/50 p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}
