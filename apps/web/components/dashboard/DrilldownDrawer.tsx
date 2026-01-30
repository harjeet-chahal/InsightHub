'use client';

import { useState, useEffect } from 'react';
import useSWR from 'swr';
import api from '@/lib/api';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DrilldownDrawerProps {
    workspaceId: string;
    brand: string;
    isOpen: boolean;
    onClose: () => void;
    onEvidenceClick: (snippet: any) => void;
}

export function DrilldownDrawer({ workspaceId, brand, isOpen, onClose, onEvidenceClick }: DrilldownDrawerProps) {
    // Fetch Evidence (Top snippets for brand)
    const [evidence, setEvidence] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen && brand) {
            setLoading(true);
            // Use search API with query matches or generic search (e.g. empty query + filters)
            // Since our search API requires a query, we can query "brand" or similar, 
            // or we can update search api to allow empty query? 
            // Current search api sorts by similarity. 
            // Let's assume we search for the brand name itself or "review" to locate generic relevant stuff.
            // Alternatively, we can assume the user wants to see "Why?" behind the stats.
            // Let's query for "positives and negatives" or similar if we wanted, but simplest is to search the brand name.

            api.post(`/workspaces/${workspaceId}/search?query=${brand}&limit=10`, {
                filters: { brand: brand }
            }).then(res => {
                setEvidence(res.data.results);
            }).finally(() => setLoading(false));
        }
    }, [isOpen, brand, workspaceId]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-y-0 right-0 z-50 w-96 bg-white shadow-2xl border-l p-6 transform transition-transform duration-300 overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">{brand} Details</h2>
                <Button variant="ghost" size="sm" onClick={onClose}><X className="h-4 w-4" /></Button>
            </div>

            <div className="space-y-6">
                <div>
                    <h3 className="font-semibold mb-2">Top Evidence Snippets</h3>
                    {loading ? <p>Loading...</p> : (
                        <ul className="space-y-3">
                            {evidence.map((item: any, i: number) => (
                                <li
                                    key={i}
                                    className="p-3 bg-gray-50 rounded border text-sm hover:bg-gray-100 cursor-pointer"
                                    onClick={() => onEvidenceClick(item)}
                                >
                                    <p className="italic mb-1">"{item.chunk_text.substring(0, 150)}..."</p>
                                    <div className="text-xs text-gray-500 flex justify-between">
                                        <span>Score: {Math.round(item.score * 100)}%</span>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
}
