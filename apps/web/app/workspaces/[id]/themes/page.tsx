'use client';

import useSWR from 'swr';
import api from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge'; // Note: Badge not created, but standard HTML/Tailwind works if missing
import { BookOpen } from 'lucide-react';

const fetcher = (url: string) => api.get(url).then((res) => res.data);

export default function ThemesPage({ params }: { params: { id: string } }) {
    const { id } = params;
    const { data: themes, isLoading } = useSWR(`/workspaces/${id}/themes`, fetcher);

    if (isLoading) return <div>Loading themes...</div>;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Themes</h2>
                <p className="text-muted-foreground">AI-extracted topics from your data.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {themes?.map((theme: any) => (
                    <Card key={theme.id} className="flex flex-col">
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <CardTitle className="text-xl">{theme.title}</CardTitle>
                                <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                                    {theme.metrics?.count} items
                                </span>
                            </div>
                            <CardDescription>{theme.summary}</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1">
                            <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
                                <BookOpen className="h-3 w-3" /> Evidence
                            </h4>
                            <ul className="space-y-2 text-sm text-gray-600 max-h-40 overflow-y-auto">
                                {theme.evidence?.map((ev: any, i: number) => (
                                    <li key={i} className="border-l-2 border-blue-200 pl-2 italic">
                                        "{ev.text.substring(0, 100)}..."
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                ))}
                {themes?.length === 0 && <p>No themes found. Run analytics first.</p>}
            </div>
        </div>
    );
}
