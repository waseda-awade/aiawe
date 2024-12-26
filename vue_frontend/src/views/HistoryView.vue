<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { EssayService } from '@/services/essayService'
import { columns } from '@/components/history/columns'
import DataTable from '@/components/history/DataTable.vue'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import type { EssayHistory } from '@/types/essay'

const ITEMS_PER_PAGE = 10
const data = ref<EssayHistory[]>([])
const totalItems = ref(0)
const currentPage = ref(1)
const selectedRecord = ref<EssayHistory | null>(null)
const showDialog = ref(false)

async function loadData(page: number) {
  try {
    const response = await EssayService.getEssayHistory(page, ITEMS_PER_PAGE)
    data.value = response.results
    totalItems.value = response.count
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

function handleRowClick(record: EssayHistory) {
  selectedRecord.value = record
  showDialog.value = true
}

onMounted(() => {
  loadData(1)
})
</script>

<template>
  <div class="container mx-auto">
    <h1 class="text-2xl font-bold mb-2">Essay History</h1>
    <p class="text-sm text-muted-foreground mb-4">Click on a row to view the details.</p>

    <DataTable :data="data" :columns="columns" @row-click="handleRowClick" />

    <Dialog :open="showDialog" @update:open="showDialog = false">
      <DialogContent class="max-w-2xl">
        <div v-if="selectedRecord" class="space-y-4">
          <div>
            <h3 class="font-medium">Essay</h3>
            <p class="mt-1">{{ selectedRecord.essay }}</p>
          </div>
          <div>
            <h3 class="font-medium">Score</h3>
            <p class="mt-1">{{ selectedRecord.result }}</p>
          </div>
          <div>
            <h3 class="font-medium">Status</h3>
            <p class="mt-1">{{ selectedRecord.status }}</p>
          </div>
          <div>
            <h3 class="font-medium">Created At</h3>
            <p class="mt-1">{{ new Date(selectedRecord.created_at).toLocaleString() }}</p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
