'use client';

import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Download, FileSpreadsheet, Presentation } from 'lucide-react';

export default function ExportsPage({ params }: { params: { id: string } }) {
    const { id } = params;

    async function downloadCSV() {
        try {
            const response = await api.get(`/workspaces/${id}/export/csv`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'export.zip'); // or filename from header
            document.body.appendChild(link);
            link.click();
        } catch (e) {
            console.error(e);
            alert('Download failed');
        }
    }

    async function downloadPPTX() {
        try {
            const response = await api.get(`/workspaces/${id}/export/pptx`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'report.pptx');
            document.body.appendChild(link);
            link.click();
        } catch (e) {
            console.error(e);
            alert('Download failed');
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Exports</h2>
                <p className="text-muted-foreground">Download your insights and reports.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <FileSpreadsheet className="h-5 w-5 text-green-600" />
                            Raw Data (CSV)
                        </CardTitle>
                        <CardDescription>
                            Zip archive containing filtered sources, claims, sentiment data, and scorecard results.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button onClick={downloadCSV} className="w-full">
                            <Download className="mr-2 h-4 w-4" /> Download ZIP
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Presentation className="h-5 w-5 text-orange-600" />
                            Presentation (PPTX)
                        </CardTitle>
                        <CardDescription>
                            10-slide PowerPoint deck with executive summary, charts, and recommendations.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button onClick={downloadPPTX} className="w-full" variant="secondary">
                            <Download className="mr-2 h-4 w-4" /> Download PPTX
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
