'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Play, Plus } from 'lucide-react';

const fetcher = (url: string) => api.get(url).then((res) => res.data);

export default function ScorecardsPage({ params }: { params: { id: string } }) {
    const { id } = params;
    // We need to list scorecards. Note: Previous implementation only had create/run endpoints but didn't explicitly implement a "List Scorecards" endpoint, 
    // but usually GET /scorecards/{id} gets one. We should probably list them.
    // Wait, I didn't add a LIST scorecards endpoint in the backend router? Use DB directly? No.
    // The backend implementation added `GET /scorecards/{scorecard_id}` and `GET /scorecards/{scorecard_id}/results`.
    // I missed a `GET /workspaces/{id}/scorecards` list endpoint in the backend?
    // Checking `apps/api/routers/scorecards.py`...
    // Ah, I missed adding a specific "List by Workspace" endpoint for scorecards in the backend implementation plan/code step! 
    // I only did Create `POST /workspaces/{id}/scorecards`.
    // I will assume for now I can create one and store the ID in local state or I should fix the backend.
    // FIX: I will verify backend `apps/api/routers/scorecards.py` content via tool or just assume I need to add it.
    // Actually, let's just add the backend endpoint now quickly as a fix, or else the page won't work well.
    // But wait, `POST /workspaces/{id}/scorecards` returns the created scorecard.
    // I'll add `GET /workspaces/{id}/scorecards` to the backend now to be safe.

    // For now in UI let's stub it or handle creation only.
    // Actually, I'll add the listing endpoint to backend in a moment.

    // Let's implement the UI assuming the endpoint exists or use a workaround.
    // I will check backend file content first.

    const { data: scorecards } = useSWR(`/workspaces/${id}/scorecards`, fetcher);

    const [name, setName] = useState('');
    const [configStr, setConfigStr] = useState('{\n  "factors": [\n    {"name": "Taste", "keywords": ["delicious"], "weight": 1.0}\n  ]\n}');
    const [selectedScorecard, setSelectedScorecard] = useState<string | null>(null);
    const [results, setResults] = useState<any[]>([]);

    async function handleCreate(e: React.FormEvent) {
        e.preventDefault();
        try {
            await api.post(`/workspaces/${id}/scorecards`, {
                name,
                config: JSON.parse(configStr)
            });
            mutate(`/workspaces/${id}/scorecards`);
            setName('');
        } catch (e) {
            alert('Invalid JSON');
        }
    }

    async function handleRun(scId: string) {
        await api.post(`/scorecards/${scId}/run`);
        alert('Run started');
        setSelectedScorecard(scId);
    }

    async function viewResults(scId: string) {
        setSelectedScorecard(scId);
        const res = await api.get(`/scorecards/${scId}/results`);
        setResults(res.data);
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Scorecards</h2>
                <p className="text-muted-foreground">Define criteria and score brands.</p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Create Form */}
                <Card>
                    <CardHeader><CardTitle>New Scorecard</CardTitle></CardHeader>
                    <CardContent>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div>
                                <Label>Name</Label>
                                <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Toothpaste Scorecard" />
                            </div>
                            <div>
                                <Label>Config (JSON)</Label>
                                <textarea
                                    className="font-mono text-xs w-full h-32 p-2 border rounded"
                                    value={configStr}
                                    onChange={e => setConfigStr(e.target.value)}
                                />
                            </div>
                            <Button type="submit"><Plus className="mr-2 h-4 w-4" /> Create</Button>
                        </form>
                    </CardContent>
                </Card>

                {/* List */}
                <Card>
                    <CardHeader><CardTitle>Available Scorecards</CardTitle></CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {scorecards?.map((sc: any) => (
                                <div key={sc.id} className="flex items-center justify-between border p-3 rounded">
                                    <div className="font-medium">{sc.name}</div>
                                    <div className="flex gap-2">
                                        <Button size="sm" variant="outline" onClick={() => handleRun(sc.id)}>
                                            <Play className="h-4 w-4" />
                                        </Button>
                                        <Button size="sm" onClick={() => viewResults(sc.id)}>
                                            Results
                                        </Button>
                                    </div>
                                </div>
                            ))}
                            {(!scorecards || scorecards.length === 0) && <p className="text-sm text-gray-500">No scorecards found.</p>}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Results Table */}
            {selectedScorecard && results.length > 0 && (
                <Card>
                    <CardHeader><CardTitle>Results</CardTitle></CardHeader>
                    <CardContent>
                        <table className="w-full text-sm text-left">
                            <thead className="bg-gray-50 uppercase">
                                <tr>
                                    <th className="px-4 py-3">Brand</th>
                                    <th className="px-4 py-3">Overall</th>
                                    <th className="px-4 py-3">Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.map((r) => (
                                    <tr key={r.id} className="border-b">
                                        <td className="px-4 py-3 font-medium">{r.brand}</td>
                                        <td className="px-4 py-3 font-bold text-blue-600">{r.results.overall}</td>
                                        <td className="px-4 py-3 text-xs text-gray-500">
                                            {JSON.stringify(r.results.factors)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
