<template>
  <div class="flex flex-col gap-6 md:flex-row max-w-7xl mx-auto">
    <Card class="flex-1">
      <CardHeader>
        <CardTitle class="mb-4">Evaluate your essay</CardTitle>
        <CardDescription>
          <p>AiAWE works best assessing argumentative writing that is under 1,000 words.</p>
          <p>The score produced by AiAWE is based on the
            <router-link to="/rubric" class="text-blue-500 hover:underline">
              ETS TOEFL Independent Writing Rubric
            </router-link>.
          </p>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="handleSubmit" class="space-y-4">
          <!-- Model selector: authenticated users only -->
          <FormField
            v-if="isAuthenticated"
            v-slot="{ componentField }"
            name="model_id"
          >
            <FormItem>
              <div class="text-muted-foreground">1. Please choose the LLM that will assess your writing from the drop down menu.</div>
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

          <FormField
            v-slot="{ componentField }"
            name="essay_topic"
          >
            <FormItem>
              <div class="text-muted-foreground">
                {{ isAuthenticated ? '2.' : '1.' }} Enter the topic of your essay.
              </div>
              <FormControl>
                <Input
                  v-bind="componentField"
                  placeholder="e.g., 'Do you agree or disagree with the following statement? ...'"
                  :disabled="isProcessing || isPending"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <div class="text-muted-foreground">
            {{ isAuthenticated ? '3.' : '2.' }} Upload a Word document or enter your text directly.
          </div>
          <FileUpload accept=".docx,.doc" :loading="isProcessing" :disabled="isLoading"
            @file-selected="handleFileSelected" />

          <FormField
            v-slot="{ componentField }"
            name="essay"
          >
            <FormItem>
              <FormControl>
                <Textarea
                  ref="essayTextarea"
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
              <ScrollArea class="text-sm flex flex-col overflow-y-auto mt-2 px-4 py-2 rounded-lg border border-gray-200 bg-gray-100/50">
                <div class="pr-4 whitespace-pre-wrap">
                  {{ currentRequest?.reasoning }}
                </div>
              </ScrollArea>
            </div>
            <p v-if="isFailed" class="text-sm text-destructive mt-2">
              {{ currentRequest?.error }}
            </p>
          </div>

          <!-- Anonymous post-result CTA -->
          <div
            v-if="isCompleted && !isAuthenticated"
            class="rounded-lg border border-brand/30 bg-brand/5 p-4 text-sm text-center"
          >
            <router-link :to="{ name: 'signup' }" class="font-semibold text-brand hover:underline">
              Create a free account
            </router-link>
            to save this evaluation and access additional models.
          </div>

          <p v-if="generalError" class="text-destructive text-sm">{{ generalError }}</p>

          <!-- Turnstile widget: anonymous users only -->
          <div v-if="!isAuthenticated" ref="turnstileContainer" class="flex justify-center py-1" />

          <Button
            type="submit"
            class="w-full"
            :disabled="isLoading || isProcessing || isPending || !form.meta.value.valid || (!isAuthenticated && !turnstileToken)"
          >
            <Loader2 v-if="isLoading || isPending" class="mr-2 h-4 w-4 animate-spin" />
            {{ isLoading ? 'Submitting...' : isPending ? 'Processing...' : 'Submit' }}
          </Button>

          <Button
            v-if="isLoading || isPending || isCompleted"
            variant="outline"
            type="button"
            class="w-full mt-2"
            @click="handleReset"
          >
            Make a new submission
          </Button>
        </form>
      </CardContent>
    </Card>

    <!-- Recent evaluations: authenticated users only -->
    <div v-if="isAuthenticated" class="w-full md:w-60 md:shrink-0">
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

// Cloudflare Turnstile (anonymous users only)
const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY as string
const turnstileContainer = ref<HTMLElement | null>(null)
const turnstileToken = ref('')
const turnstileWidgetId = ref<string | number | null>(null)

const loadTurnstileScript = (): Promise<void> => {
  return new Promise((resolve) => {
    if ((window as any).turnstile) { resolve(); return }
    let script = document.getElementById('cf-turnstile-script') as HTMLScriptElement | null
    if (!script) {
      script = document.createElement('script')
      script.id = 'cf-turnstile-script'
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
      script.async = true
      script.defer = true
      document.head.appendChild(script)
    }
    script.addEventListener('load', () => resolve(), { once: true })
  })
}

const initTurnstile = async () => {
  await loadTurnstileScript()
  await nextTick()
  if (!turnstileContainer.value || !(window as any).turnstile) return
  turnstileWidgetId.value = (window as any).turnstile.render(turnstileContainer.value, {
    sitekey: TURNSTILE_SITE_KEY,
    callback: (token: string) => { turnstileToken.value = token },
    'expired-callback': () => { turnstileToken.value = '' },
    'error-callback': () => { turnstileToken.value = '' },
  })
}

const resetTurnstile = () => {
  if (turnstileWidgetId.value !== null && (window as any).turnstile) {
    (window as any).turnstile.reset(turnstileWidgetId.value)
  }
  turnstileToken.value = ''
}

const form = useForm({
  validationSchema: toTypedSchema(essayFormSchema),
  initialValues: {
    essay: '',
    essay_topic: '',
    model_id: '',
  },
})

const NUM_HISTORY_ITEMS = 5
const { toast } = useToast()
const { processDocument, isProcessing } = useDocumentProcessor()

const essayTextarea = ref<typeof Textarea | null>(null)
const generalError = ref('')
const charCount = computed(() => form.values.essay?.length || 0)
const isOverLimit = computed(() => charCount.value > MAX_CHARS)
const isLoading = ref(false)
const isPending = computed(() => currentRequest.value?.status === 'PENDING')
const isCompleted = computed(() => currentRequest.value?.status === 'COMPLETED')
const isFailed = computed(() => currentRequest.value?.status === 'FAILED')

const currentRequest = ref<EssayRequest | null>(null)
const pollingInterval = ref<ReturnType<typeof setInterval> | null>(null)
const anonymousPollingTimer = ref<ReturnType<typeof setTimeout> | null>(null)

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
    if (!isAuthenticated.value) {
      // Anonymous: auto-select the single available public model
      if (models.length > 0) {
        form.setFieldValue('model_id', models[0].id.toString())
      }
      return
    }
    const updatedSelectedModel = models.find(model => model.id.toString() === selectedModel.value)
    if (!updatedSelectedModel) {
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
  if (!isAuthenticated.value) {
    await updateModelQuotas()
    await initTurnstile()
    return
  }

  await Promise.all([
    updateModelQuotas(),
    loadRecentHistory()
  ])

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

      if (currentRequest.value) {
        const updatedRequest = results.find(r => r.id === currentRequest.value?.id)
        if (updatedRequest) {
          currentRequest.value = updatedRequest
        }
      }

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

const startAnonymousPolling = (requestId: number) => {
  let attempts = 0
  const poll = async () => {
    try {
      const request = await EssayService.getEssay(requestId)
      currentRequest.value = request
      if (request.status === 'COMPLETED') {
        toast({
          title: 'Evaluation Complete',
          description: `Your essay score: ${request.score}`,
        })
        return
      }
      if (request.status === 'FAILED') {
        toast({
          title: 'Evaluation Failed',
          description: request.error || 'Unknown error',
          variant: 'destructive',
        })
        return
      }
      const delay = Math.min(500 * Math.pow(2, attempts), 10000)
      attempts++
      anonymousPollingTimer.value = setTimeout(poll, delay)
    } catch (err) {
      console.error('Error polling anonymous request:', err)
    }
  }
  poll()
}

const handleSubmit = form.handleSubmit(async (values) => {
  generalError.value = ''
  isLoading.value = true

  try {
    const response = await EssayService.submitEssay({
      essay: values.essay,
      essay_topic: values.essay_topic,
      model_id: Number(values.model_id),
      ...(!isAuthenticated.value ? { turnstile_token: turnstileToken.value } : {}),
    })
    currentRequest.value = response

    if (isAuthenticated.value) {
      await loadRecentHistory()
      startHistoryPolling()
    } else {
      startAnonymousPolling(response.id)
    }

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
    if (!isAuthenticated.value) {
      resetTurnstile()
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
  form.setFieldValue('essay_topic', '')
  currentRequest.value = null
  generalError.value = ''

  if (isAuthenticated.value) {
    const response = await EssayService.getEssayHistory(1, NUM_HISTORY_ITEMS)
    recentHistory.value = response.results

    const hasPendingRequests = response.results.some(r => r.status === 'PENDING')
    if (hasPendingRequests) {
      startHistoryPolling()
    }
  } else {
    resetTurnstile()
  }

  setTimeout(() => {
    essayTextarea.value?.focus()
  }, 0)
}

onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
  if (anonymousPollingTimer.value) {
    clearTimeout(anonymousPollingTimer.value)
  }
})
</script>
