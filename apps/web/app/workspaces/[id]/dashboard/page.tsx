import DashboardClient from '@/components/dashboard/DashboardClient';

export default function DashboardPage({ params }: { params: { id: string } }) {
    return <DashboardClient workspaceId={params.id} />;
}
import api from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, LineChart, Line } from 'recharts';
import { RefreshCw } from 'lucide-react';

const fetcher = (url: string) => api.get(url).then((res) => res.data);

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function DashboardPage({ params }: { params: { id: string } }) {
    const { id } = params;
    const { data, mutate, isLoading } = useSWR(`/workspaces/${id}/dashboard`, fetcher);

    async function handleRefresh() {
        await api.post(`/workspaces/${id}/analytics`);
        alert('Analytics job started. Check back in a moment.');
    }

    if (isLoading) return <div>Loading dashboard...</div>;

    const stats = data?.stats;
    const claims = data?.claims;
    const trends = data?.trends;

    // Prepare Chart Data
    const sentimentData = stats?.sentiment_distribution ? Object.entries(stats.sentiment_distribution).map(([name, value]) => ({ name, value })) : [];
    const claimsData = claims ? Object.entries(claims)
        .sort(([, a]: any, [, b]: any) => b - a)
        .slice(0, 10)
        .map(([name, value]) => ({ name, value })) : [];

    // Trends data is complex (nested keys). Let's just visualize one brand or flatten for simplicity if possible.
    // Trends: { "BrandA": { "2023-01": 4.5 }, "BrandB": ... }
    // We need to transform to array: [{date: "2023-01", BrandA: 4.5, BrandB: ...}]
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

            <div className="grid gap-4 md:grid-cols-2">
                {/* Sentiment Chart */}
                <Card>
                    <CardHeader><CardTitle>Sentiment Distribution</CardTitle></CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={sentimentData}
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                    label
                                >
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

                {/* Claims Chart */}
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
        </div>
    );
}
