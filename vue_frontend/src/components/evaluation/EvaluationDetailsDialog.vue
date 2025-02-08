<script setup lang="ts">
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { EssayRequest } from '@/types/essay'

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
      <ScrollArea class="h-full max-h-[70vh]">
        <div v-if="record" class="space-y-4">
          <h2 class="text-2xl font-bold">Evaluation Details</h2>
          <div>
            <h3 class="font-medium">Essay</h3>
            <p class="mt-1">{{ record.essay }}</p>
          </div>
          <div>
            <h3 class="font-medium">Score</h3>
            <p class="mt-1">{{ record.score }}</p>
          </div>
          <div>
            <h3 class="font-medium">Reasoning</h3>
            <p class="mt-1">{{ record.reasoning }}</p>
          </div>
          <div>
            <h3 class="font-medium">Status</h3>
            <p class="mt-1">{{ record.status }}</p>
          </div>
          <div>
            <h3 class="font-medium">Created At</h3>
            <p class="mt-1">{{ new Date(record.created_at).toLocaleString() }}</p>
          </div>
        </div>
      </ScrollArea>
    </DialogContent>
  </Dialog>
</template>
