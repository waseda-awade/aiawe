import { type ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import type { EssayRequest } from '@/types/essay'
import { Checkbox } from '@/components/ui/checkbox'

export const columns: ColumnDef<EssayRequest>[] = [
  {
    id: 'select',
    header: ({ table }) => h(Checkbox, {
      'checked': table.getIsAllPageRowsSelected(),
      'onUpdate:checked': (value: boolean) => table.toggleAllPageRowsSelected(!!value),
      'ariaLabel': 'Select all',
    }),
    cell: ({ row }) => h(Checkbox, {
      'checked': row.getIsSelected(),
      'onUpdate:checked': (value: boolean) => row.toggleSelected(!!value),
      'ariaLabel': 'Select row',
    }),
    enableSorting: false,
    enableHiding: false,
  },
  {
    id: 'sequence',
    header: '#',
    cell: ({ row }) => {
      return row.index + 1
    },
  },
  {
    accessorKey: 'essay',
    header: 'Essay',
    cell: ({ row }) => {
      const essay = row.getValue('essay') as string
      return h(
        'div',
        { class: 'max-w-80 truncate' },
        essay,
      )
    },
  },
  {
    accessorKey: 'reasoning',
    header: 'Reasoning',
    cell: ({ row }) => {
      const reasoning = row.getValue('reasoning') as string
      return h(
        'div',
        { class: 'max-w-80 truncate' },
        reasoning,
      )
    },
  },
  {
    accessorKey: 'score',
    header: 'Score',
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status = row.getValue('status') as string
      return h(
        'div',
        {
          class: {
            'text-green-600': status === 'COMPLETED',
            'text-red-600': status === 'FAILED',
            'text-yellow-600': status === 'PENDING',
          },
        },
        status,
      )
    },
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ row }) => {
      return new Date(row.getValue('created_at')).toLocaleString()
    },
    sortingFn: 'datetime',
  },
]
