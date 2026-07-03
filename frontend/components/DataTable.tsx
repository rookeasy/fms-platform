import type { ReactNode } from "react";

export type DataTableColumn<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
};

type DataTableProps<T> = {
  columns: Array<DataTableColumn<T>>;
  rows: T[];
};

export function DataTable<T>({ columns, rows }: DataTableProps<T>) {
  return (
    <div className="fop-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/10 text-sm">
          <thead className="bg-white/[0.035]">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {rows.map((row, index) => (
              <tr key={index} className="transition hover:bg-white/[0.045]">
                {columns.map((column) => (
                  <td key={column.key} className="px-5 py-4 text-[#B6C1CF]">
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
