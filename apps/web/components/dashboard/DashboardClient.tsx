'use client';

import { useState } from 'react';
import useSWR from 'swr';
import api from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { BrandTable } from './BrandTable';
import { DrilldownDrawer } from './DrilldownDrawer';
import { EvidenceModal } from './EvidenceModal';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, LineChart, Line } from 'recharts';

const fetcher = (url: string) => api.get(url).then((res) => res.data);
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function DashboardClient({ workspaceId }: { workspaceId: string }) {
    const { data, isLoading, mutate } = useSWR(`/workspaces/${workspaceId}/dashboard`, fetcher);

    const [selectedBrand, setSelectedBrand] = useState<string | null>(null);
    const [evidenceSnippet, setEvidenceSnippet] = useState<any | null>(null); // For modal

    if (isLoading) return <div>Loading dashboard...</div>;

    const stats = data?.stats;
    const claims = data?.claims;
    const trends = data?.trends;
    const brandsSummary = stats?.brands_summary || {};

    // --- Chart Data Preparation ---
    const sentimentData = stats?.sentiment_distribution ? Object.entries(stats.sentiment_distribution).map(([name, value]) => ({ name, value })) : [];
    const claimsData = claims ? Object.entries(claims)
        .sort(([, a]: any, [, b]: any) => b - a)
        .slice(0, 10)
        .map(([name, value]) => ({ name, value })) : [];

    const trendDates = new Set<string>();
    if (trends) {
        Object.values(trends).forEach((months: any) => Object.keys(months).forEach(d => trendDates.add(d)));
    }
    const sortedDates = Array.from(trendDates).sort();
    const trendsData = sortedDates.map(date => {
        const entry: any = { date };
        if (trends) {
            Object.entries(trends).forEach(([brand, months]: any) => {
                if (months[date]) entry[brand] = months[date];
            });
        }
        return entry;
    });

    async function handleRefresh() {
        await api.post(`/workspaces/${workspaceId}/analytics`);
        alert('Analytics job started. Check back in a moment.');
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                    <p className="text-muted-foreground">High-level insights at a glance.</p>
                </div>
                <Button onClick={handleRefresh}>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Run Analytics
                </Button>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_documents || 0}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Avg Sentiment</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.average_sentiment || 0}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Charts Row */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader><CardTitle>Sentiment Distribution</CardTitle></CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={sentimentData} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value" label>
                                    {sentimentData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader><CardTitle>Top Claims</CardTitle></CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={claimsData} layout="vertical">
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip />
                                <Bar dataKey="value" fill="#82ca9d" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>

            {/* Trends Chart */}
            <Card>
                <CardHeader><CardTitle>Ratings Trends</CardTitle></CardHeader>
                <CardContent className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={trendsData}>
                            <XAxis dataKey="date" />
                            <YAxis domain={[0, 5]} />
                            <Tooltip />
                            <Legend />
                            {trends && Object.keys(trends).map((brand, i) => (
                                <Line key={brand} type="monotone" dataKey={brand} stroke={COLORS[i % COLORS.length]} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Brand Table */}
            <Card>
                <CardHeader><CardTitle>Brand Analysis</CardTitle></CardHeader>
                <CardContent>
                    <BrandTable
                        data={Object.entries(brandsSummary).map(([brand, data]: any) => ({ brand, ...data }))}
                        onBrandClick={setSelectedBrand}
                    />
                </CardContent>
            </Card>

            {/* Interactive Elements */}
            {selectedBrand && (
                <DrilldownDrawer
                    workspaceId={workspaceId}
                    brand={selectedBrand}
                    isOpen={!!selectedBrand}
                    onClose={() => setSelectedBrand(null)}
                    onEvidenceClick={setEvidenceSnippet}
                />
            )}

            {evidenceSnippet && (
                <EvidenceModal
                    snippet={evidenceSnippet}
                    isOpen={!!evidenceSnippet}
                    onClose={() => setEvidenceSnippet(null)}
                />
            )}
        </div>
    );
}
