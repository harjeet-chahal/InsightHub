'use client';

import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    ColumnDef
} from '@tanstack/react-table';

interface BrandData {
    brand: string;
    total_docs: number;
    avg_sentiment: number;
    avg_rating: number;
    top_claim: string;
}

interface BrandTableProps {
    data: BrandData[];
    onBrandClick: (brand: string) => void;
}

export function BrandTable({ data, onBrandClick }: BrandTableProps) {
    const columns: ColumnDef<BrandData>[] = [
        { accessorKey: 'brand', header: 'Brand' },
        { accessorKey: 'total_docs', header: 'Reviews' },
        { accessorKey: 'avg_rating', header: 'Avg Rating' },
        { accessorKey: 'avg_sentiment', header: 'Sentiment' },
        { accessorKey: 'top_claim', header: 'Top Claim' },
    ];

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    return (
        <div className="rounded-md border">
            <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                    {table.getHeaderGroups().map(headerGroup => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map(header => (
                                <th key={header.id} className="p-3 text-left font-medium">
                                    {flexRender(header.column.columnDef.header, header.getContext())}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody>
                    {table.getRowModel().rows.map(row => (
                        <tr
                            key={row.id}
                            onClick={() => onBrandClick(row.original.brand)}
                            className="border-b hover:bg-gray-50 cursor-pointer"
                        >
                            {row.getVisibleCells().map(cell => (
                                <td key={cell.id} className="p-3">
                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
