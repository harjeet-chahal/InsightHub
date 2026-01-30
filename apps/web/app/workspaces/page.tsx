'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import Link from 'next/link';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, ArrowRight } from 'lucide-react';

const fetcher = (url: string) => api.get(url).then((res) => res.data);

export default function WorkspacesPage() {
    const { data: workspaces, error } = useSWR('/workspaces', fetcher);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [isCreating, setIsCreating] = useState(false);

    async function handleCreate(e: React.FormEvent) {
        e.preventDefault();
        if (!newWorkspaceName.trim()) return;

        setIsCreating(true);
        try {
            await api.post('/workspaces', { name: newWorkspaceName });
            mutate('/workspaces');
            setNewWorkspaceName('');
        } catch (err) {
            console.error(err);
        } finally {
            setIsCreating(false);
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="mx-auto max-w-5xl space-y-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Workspaces</h1>
                        <p className="text-muted-foreground">Manage your research projects.</p>
                    </div>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>Create New Workspace</CardTitle>
                        <CardDescription>Start a new project container.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleCreate} className="flex gap-4 items-end">
                            <div className="grid w-full max-w-sm items-center gap-1.5">
                                <Label htmlFor="name">Name</Label>
                                <Input
                                    id="name"
                                    placeholder="e.g. Toothpaste Market Research"
                                    value={newWorkspaceName}
                                    onChange={(e) => setNewWorkspaceName(e.target.value)}
                                />
                            </div>
                            <Button type="submit" disabled={isCreating}>
                                {isCreating ? 'Creating...' : <><Plus className="mr-2 h-4 w-4" /> Create</>}
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {workspaces?.map((ws: any) => (
                        <Link key={ws.id} href={`/workspaces/${ws.id}/dashboard`}>
                            <Card className="h-full transition-all hover:border-blue-500 hover:shadow-md cursor-pointer group">
                                <CardHeader>
                                    <CardTitle className="flex items-center justify-between">
                                        {ws.name}
                                        <ArrowRight className="h-4 w-4 opacity-0 transition-opacity group-hover:opacity-100" />
                                    </CardTitle>
                                    <CardDescription>Created {new Date(ws.created_at).toLocaleDateString()}</CardDescription>
                                </CardHeader>
                            </Card>
                        </Link>
                    ))}
                    {!workspaces && !error && <p>Loading...</p>}
                    {workspaces?.length === 0 && (
                        <p className="text-gray-500 col-span-full text-center py-10">No workspaces found. Create one above!</p>
                    )}
                </div>
            </div>
        </div>
    );
}
