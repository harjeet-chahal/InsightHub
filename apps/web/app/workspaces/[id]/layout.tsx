'use client';

import DashboardLayout from '@/components/layout/DashboardLayout';

export default function Layout({
    children,
    params,
}: {
    children: React.ReactNode;
    params: { id: string };
}) {
    return (
        <DashboardLayout workspaceId={params.id}>
            {children}
        </DashboardLayout>
    );
}
