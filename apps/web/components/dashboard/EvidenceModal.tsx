'use client';

import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function EvidenceModal({ snippet, isOpen, onClose }: { snippet: any; isOpen: boolean; onClose: () => void }) {
    if (!isOpen || !snippet) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full p-6 relative animate-in fade-in zoom-in duration-200">
                <Button variant="ghost" size="sm" className="absolute top-4 right-4" onClick={onClose}>
                    <X className="h-4 w-4" />
                </Button>

                <h3 className="text-xl font-bold mb-4">Evidence Detail</h3>

                <div className="space-y-4">
                    <div className="bg-blue-50 p-4 rounded-md border border-blue-100">
                        <p className="text-lg leading-relaxed">{snippet.chunk_text}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div>
                            <span className="font-semibold">Source:</span> {snippet.source_title}
                        </div>
                        <div>
                            <span className="font-semibold">Match Score:</span> {Math.round(snippet.score * 100)}%
                        </div>
                        {snippet.source_url && (
                            <div className="col-span-2">
                                <a href={snippet.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800">
                                    View Original Source
                                </a>
                            </div>
                        )}
                    </div>
                </div>

                <div className="mt-6 flex justify-end">
                    <Button onClick={onClose}>Close</Button>
                </div>
            </div>
        </div>
    );
}
