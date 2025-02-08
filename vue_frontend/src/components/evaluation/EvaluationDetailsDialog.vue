<script setup lang="ts">
import { Dialog, DialogContent } from '@/components/ui/dialog'
import type { EssayRequest } from '@/types/essay'
import { ScrollArea } from '@/components/ui/scroll-area'

defineProps<{
  open: boolean
  record: EssayRequest | null
}>()

defineEmits<{
  'update:open': [value: boolean]
}>()
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-2xl max-h-[80vh]">
      <div v-if="record" class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <h2 class="text-2xl font-bold">Evaluation Details</h2>
          <!-- Status and date -->
          <div class="flex flex-col sm:flex-row sm:items-end gap-4 text-sm text-muted-foreground">
            <div>
              <span class="font-medium text-foreground">Status: </span>
              <span :class="{
                'text-yellow-500': record.status === 'PENDING',
                'text-green-500': record.status === 'COMPLETED',
                'text-red-500': record.status === 'FAILED',
              }">
                {{ record.status }}
              </span>
            </div>
            <div>
              <span class="font-medium text-foreground">Created: </span>
              {{ new Date(record.created_at).toLocaleString() }}
            </div>
          </div>
        </div>

        <!-- Error message -->
        <p v-if="record.status === 'FAILED'" class="text-sm text-destructive">
          {{ record.error }}
        </p>

        <!-- Score section -->
        <div v-if="record.status === 'COMPLETED'" class="mb-2">
          <p class="text-4xl font-semibold text-green-600">
            Score: {{ record.score }}
          </p>
        </div>

        <!-- Reasoning section -->
        <div v-if="record.status === 'COMPLETED'">
          <span class="font-semibold">Reasoning:</span>
          <ScrollArea class="text-sm flex max-h-[150px] flex-col overflow-y-auto mt-2 px-4 py-2 rounded-lg border border-gray-200 bg-gray-100/50 shadow-sm">
            <div class="pr-4">
              {{ record.reasoning }}
            </div>
          </ScrollArea>
        </div>
        <!-- Essay section with scroll -->
        <div>
          <h3 class="font-medium mb-2">Essay</h3>
          <ScrollArea class="text-sm flex max-h-[150px] flex-col overflow-y-auto mt-2 px-4 py-2 border border-gray-200 rounded-lg">
            <div class="pr-4">
              {{ record.essay }}
            </div>
          </ScrollArea>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
