<template>
  <div class="flex flex-col gap-6 md:flex-row max-w-7xl mx-auto">
    <Card class="flex-1">
      <CardHeader>
        <CardTitle>Evaluate your essay</CardTitle>
        <CardDescription> Enter your text directly or upload a Word document </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="handleSubmit" class="space-y-4">
          <FormField
            v-slot="{ componentField }"
            name="model_id"
          >
            <FormItem>
              <FormLabel>Please choose the LLM that will access your writing from the drop down menu.</FormLabel>
              <Select
                v-bind="componentField"
                :disabled="isProcessing || isPending"
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem
                      v-for="model in modelOptions"
                      :key="model.id"
                      :value="model.id.toString()"
                    >
                      {{ model.display_name }}
                      <span
                        v-if="model.daily_limit"
                        :class="{
                          'text-red-500': model.used_quota >= model.daily_limit,
                          'text-muted-foreground': model.used_quota < model.daily_limit
                        }"
                        class="ml-2"
                      >
                        ({{ model.used_quota }}/{{ model.daily_limit }})
                      </span>
                    </SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          </FormField>

          <FileUpload accept=".docx,.doc" :loading="isProcessing" :disabled="isLoading"
            @file-selected="handleFileSelected" />

          <FormField
            v-slot="{ componentField }"
            name="essay"
          >
            <FormItem>
              <FormControl>
                <Textarea
                  v-bind="componentField"
                  :rows="15"
                  placeholder="Enter your text here or upload a document..."
                  :disabled="isProcessing || isPending"
                />
              </FormControl>
              <FormMessage />
              <div class="flex justify-between items-center text-sm">
                <p class="text-muted-foreground" :class="{ invisible: !currentRequest }">
                  Status:
                  <span :class="{
                    'text-yellow-500': isPending,
                    'text-green-500': isCompleted,
                    'text-red-500': isFailed,
                  }">
                    {{ currentRequest?.status }}
                  </span>
                </p>
                <p class="text-muted-foreground" :class="{ 'text-destructive': isOverLimit }">
                  {{ charCount }}/{{ MAX_CHARS }}
                </p>
              </div>
            </FormItem>
          </FormField>

          <div v-if="currentRequest">
            <p v-if="isCompleted" class="mb-2 text-4xl font-semibold text-green-600 mt-2">
              Score: {{ currentRequest?.score }}
            </p>
            <div v-if="isCompleted">
              <span class="font-semibold">Reasoning:</span>
              <ScrollArea class="text-sm flex max-h-40 flex-col overflow-y-auto mt-2 px-4 py-2 rounded-lg border border-gray-200 bg-gray-100/50">
                <div class="pr-4">
                  {{ currentRequest?.reasoning }}
                </div>
              </ScrollArea>
            </div>
            <p v-if="isFailed" class="text-sm text-destructive mt-2">
              {{ currentRequest?.error }}
            </p>
          </div>

          <p v-if="generalError" class="text-destructive text-sm">{{ generalError }}</p>

          <Button
            type="submit"
            class="w-full"
            :disabled="isLoading || isProcessing || isPending || !form.meta.value.valid"
          >
            <Loader2 v-if="isLoading || isPending" class="mr-2 h-4 w-4 animate-spin" />
            {{ isLoading ? 'Submitting...' : isPending ? 'Processing...' : 'Submit' }}
          </Button>

          <Button
            v-if="isLoading || isPending"
            type="button"
            class="w-full mt-2"
            @click="handleReset"
          >
            Make a new submission
          </Button>
        </form>
      </CardContent>
    </Card>

    <div class="w-full md:w-60 md:shrink-0">
      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Recent Evaluations</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div
              v-for="(item, idx) in recentHistory"
              :key="item.id"
              class="px-3 py-2 rounded-lg border cursor-pointer hover:bg-muted/50 transition-colors"
              @click="handleHistoryItemClick(item)"
            >
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">#{{ idx + 1 }}</span>
                <span
                  v-if="item.status !== 'COMPLETED'"
                  :class="{
                    'text-yellow-500': item.status === 'PENDING',
                    'text-red-500': item.status === 'FAILED'
                  }"
                  class="text-xs"
                >
                  {{ item.status }}
                </span>
                <span v-else class="text-green-600 font-medium">
                  Score: {{ item.score }}
                </span>
              </div>
            </div>
            <div v-if="recentHistory.length === 0">
              <p class="text-sm text-muted-foreground">(No recent evaluations)</p>
            </div>
          </div>

          <router-link
            :to="{ name: 'history' }"
            class="flex items-center justify-center w-full mt-4 text-sm text-muted-foreground hover:text-primary"
          >
            View all history
            <ArrowRight class="w-4 h-4 ml-1" />
          </router-link>
        </CardContent>
      </Card>
    </div>

    <EvaluationDetailsDialog
      :open="showHistoryDialog"
      :record="selectedHistoryRecord"
      @update:open="showHistoryDialog = $event"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Loader2 } from 'lucide-vue-next'
import FileUpload from '@/components/FileUpload.vue'
import { useDocumentProcessor } from '@/composables/useDocumentProcessor'
import { useToast } from '@/components/ui/toast/use-toast'
import { EssayService } from '@/services/essayService'
import type { EssayRequest } from '@/types/essay'
import { AxiosError } from 'axios'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { LLMModelService } from '@/services/llmModelService'
import type { LLMModel } from '@/types/llm'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { essayFormSchema, MAX_CHARS } from '@/lib/validations'
import EvaluationDetailsDialog from '@/components/evaluation/EvaluationDetailsDialog.vue'
import { ArrowRight } from 'lucide-vue-next'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useEssayPolling } from '@/composables/useEssayPolling'

const form = useForm({
  validationSchema: toTypedSchema(essayFormSchema),
  initialValues: {
    essay: '',
    model_id: '',
  },
})

const NUM_HISTORY_ITEMS = 5
const { toast } = useToast()
const { processDocument, isProcessing } = useDocumentProcessor()

const generalError = ref('')
const charCount = computed(() => form.values.essay?.length || 0)
const isOverLimit = computed(() => charCount.value > MAX_CHARS)
const isLoading = ref(false)
const isPending = computed(() => currentRequest.value?.status === 'PENDING')
const isCompleted = computed(() => currentRequest.value?.status === 'COMPLETED')
const isFailed = computed(() => currentRequest.value?.status === 'FAILED')

const currentRequest = ref<EssayRequest | null>(null)
const pollingInterval = ref<ReturnType<typeof setInterval> | null>(null)

const selectedModel = ref('')
const modelOptions = ref<LLMModel[]>([])

const recentHistory = ref<EssayRequest[]>([])
const selectedHistoryRecord = ref<EssayRequest | null>(null)
const showHistoryDialog = ref(false)

const { startPolling } = useEssayPolling()

const updateModelQuotas = async () => {
  try {
    const models = await LLMModelService.getActiveModels()
    modelOptions.value = models
    // Keep the same selected model but with updated quota
    const updatedSelectedModel = models.find(model => model.id.toString() === selectedModel.value)
    if (!updatedSelectedModel) {
      // If current selected model is no longer available, select default or first
      const defaultModel = models.find(model => model.is_default)
      selectedModel.value = (defaultModel?.id || models[0]?.id || 0).toString()
      form.setFieldValue('model_id', selectedModel.value)
    }
  } catch (err) {
    console.error('Error updating models:', err)
  }
}

const loadRecentHistory = async () => {
  try {
    const response = await EssayService.getEssayHistory(1, NUM_HISTORY_ITEMS)
    recentHistory.value = response.results
  } catch (error) {
    console.error('Failed to load recent history:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    updateModelQuotas(),
    loadRecentHistory()
  ])

  // Start polling if there are pending requests
  if (recentHistory.value.some(r => r.status === 'PENDING')) {
    startHistoryPolling()
  }
})

const handleFileSelected = async (file: File) => {
  generalError.value = ''
  isLoading.value = true

  try {
    const text = await processDocument(file)
    if (text.length > MAX_CHARS) {
      toast({
        description: `The uploaded document exceeds ${MAX_CHARS} characters. Only the first ${MAX_CHARS} characters will be used.`,
        variant: 'destructive',
      })
      form.setFieldValue('essay', text.slice(0, MAX_CHARS))
    } else {
      form.setFieldValue('essay', text)
    }
  } catch (err) {
    toast({
      description: "Failed to process document. Please make sure it's a valid Word document.",
      variant: 'destructive',
    })
    console.error('Error processing document:', err)
  } finally {
    isLoading.value = false
  }
}

const startHistoryPolling = () => {
  startPolling({
    page: 1,
    pageSize: NUM_HISTORY_ITEMS,
    onData: (results) => {
      recentHistory.value = results

      // Update current request if it exists in history
      if (currentRequest.value) {
        const updatedRequest = results.find(r => r.id === currentRequest.value?.id)
        if (updatedRequest) {
          currentRequest.value = updatedRequest
        }
      }

      // Update dialog content if open
      if (selectedHistoryRecord.value) {
        const updatedRecord = results.find(r => r.id === selectedHistoryRecord.value?.id)
        if (updatedRecord) {
          selectedHistoryRecord.value = updatedRecord
        }
      }
    },
    onStatusChange: async (request) => {
      if (request.id === currentRequest.value?.id) {
        if (request.status === 'COMPLETED') {
          toast({
            title: 'Evaluation Complete',
            description: `Your essay score: ${request.score}`,
          })
          await updateModelQuotas()
        } else if (request.status === 'FAILED' && request.error) {
          toast({
            title: 'Evaluation Failed',
            description: request.error,
            variant: 'destructive',
          })
        }
      }
    }
  })
}

const handleSubmit = form.handleSubmit(async (values) => {
  generalError.value = ''
  isLoading.value = true

  try {
    const response = await EssayService.submitEssay({
      essay: values.essay,
      model_id: Number(values.model_id)
    })
    currentRequest.value = response

    // Load history and start polling
    await loadRecentHistory()
    startHistoryPolling()

    toast({
      description: 'Essay submitted successfully. Processing...',
    })
  } catch (err: any) {
    if (err.fieldErrors) {
      form.setErrors(err.fieldErrors)
    }
    if (err.nonFieldError) {
      generalError.value = err.nonFieldError
    }
  } finally {
    isLoading.value = false
  }
})

const handleHistoryItemClick = (record: EssayRequest) => {
  selectedHistoryRecord.value = record
  showHistoryDialog.value = true
}

const handleReset = async () => {
  form.setFieldValue('essay', '')
  currentRequest.value = null
  generalError.value = ''

  // Check if we need to continue polling other requests
  const response = await EssayService.getEssayHistory(1, NUM_HISTORY_ITEMS)
  recentHistory.value = response.results

  const hasPendingRequests = response.results.some(r => r.status === 'PENDING')
  if (hasPendingRequests) {
    startHistoryPolling()
  }
}

// Clean up polling when component is unmounted
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
})
</script>
