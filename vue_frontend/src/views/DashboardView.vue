<template>
  <Card class="max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle>Evaluate your essay</CardTitle>
      <CardDescription> Enter your text directly or upload a Word document </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="space-y-4">
        <FileUpload
          accept=".docx,.doc"
          :loading="isProcessing"
          :disabled="isLoading"
          @file-selected="handleFileSelected"
        />

        <div class="space-y-2">
          <Textarea
            v-model="content"
            :rows="20"
            placeholder="Enter your text here or upload a document..."
            :disabled="isProcessing || isPending"
            :class="{ 'border-destructive': isOverLimit }"
          />
          <div class="flex justify-between items-center text-sm">
            <p class="text-muted-foreground" :class="{ invisible: !currentRequest }">
              Status:
              <span
                :class="{
                  'text-yellow-500': isPending,
                  'text-green-500': isCompleted,
                  'text-red-500': isFailed,
                }"
              >
                {{ currentRequest?.status }}
              </span>
            </p>
            <p class="text-muted-foreground" :class="{ 'text-destructive': isOverLimit }">
              {{ charCount }}/{{ MAX_CHARS }}
            </p>
          </div>
        </div>

        <div v-if="currentRequest">
          <p v-if="isCompleted" class="text-4xl font-semibold text-green-600 mt-2">
            Score: {{ currentRequest?.score }}
          </p>
          <p v-if="isFailed" class="text-sm text-destructive mt-2">
            {{ currentRequest?.error }}
          </p>
        </div>

        <p v-if="error" class="text-destructive text-sm">{{ error }}</p>

        <Button
          class="w-full"
          @click="handleSubmit"
          :disabled="isLoading || isProcessing || !content.trim() || isOverLimit || isPending"
        >
          <Loader2 v-if="isLoading || isPending" class="mr-2 h-4 w-4 animate-spin" />
          {{ isLoading ? 'Submitting...' : isPending ? 'Processing...' : 'Submit' }}
        </Button>
      </div>

      <router-link
        :to="{ name: 'history' }"
        class="text-sm text-muted-foreground hover:text-primary mt-2 block text-right underline"
        >View History</router-link
      >
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Loader2 } from 'lucide-vue-next'
import FileUpload from '@/components/FileUpload.vue'
import { useDocumentProcessor } from '@/composables/useDocumentProcessor'
import { useToast } from '@/components/ui/toast/use-toast'
import { EssayService } from '@/services/essayService'
import type { EssayRequest } from '@/services/essayService'
import { AxiosError } from 'axios'
const MAX_CHARS = 5000
const content = ref('')
const isLoading = ref(false)
const error = ref('')

const { toast } = useToast()
const { processDocument, isProcessing } = useDocumentProcessor()

const charCount = computed(() => content.value.length)
const isOverLimit = computed(() => charCount.value > MAX_CHARS)
const isPending = computed(() => currentRequest.value?.status === 'PENDING')
const isCompleted = computed(() => currentRequest.value?.status === 'COMPLETED')
const isFailed = computed(() => currentRequest.value?.status === 'FAILED')

const currentRequest = ref<EssayRequest | null>(null)
const pollingInterval = ref<number | null>(null)

const handleFileSelected = async (file: File) => {
  error.value = ''

  try {
    const text = await processDocument(file)
    if (text.length > MAX_CHARS) {
      toast({
        description: `The uploaded document exceeds ${MAX_CHARS} characters. Only the first ${MAX_CHARS} characters will be used.`,
        variant: 'destructive',
      })
      content.value = text.slice(0, MAX_CHARS)
    } else {
      content.value = text
    }
  } catch (err) {
    toast({
      description: "Failed to process document. Please make sure it's a valid Word document.",
      variant: 'destructive',
    })
    console.error('Error processing document:', err)
  }
}

const startPolling = (requestId: number) => {
  // Clear any existing polling
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  // Start new polling
  pollingInterval.value = setInterval(async () => {
    try {
      const data = await EssayService.getEssay(requestId)
      currentRequest.value = data

      if (data.status !== 'PENDING') {
        // Stop polling if we're no longer pending
        if (pollingInterval.value) {
          clearInterval(pollingInterval.value)
          pollingInterval.value = null
        }

        // Show result or error
        if (data.status === 'COMPLETED') {
          toast({
            title: 'Evaluation Complete',
            description: `Your essay score: ${data.result}`,
          })
        } else if (data.error) {
          toast({
            title: 'Evaluation Failed',
            description: data.error,
            variant: 'destructive',
          })
        }
      }
    } catch (err) {
      console.error('Error polling status:', err)
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
        pollingInterval.value = null
      }
      toast({
        description: 'Failed to get evaluation status',
        variant: 'destructive',
      })
    }
  }, 3000) // Poll every 3 seconds
}

const handleSubmit = async () => {
  if (!content.value.trim()) {
    error.value = 'Please enter some text before submitting.'
    return
  }

  if (isOverLimit.value) {
    error.value = `Text exceeds maximum length of ${MAX_CHARS} characters.`
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await EssayService.submitEssay(content.value)
    currentRequest.value = response

    // Start polling for status
    startPolling(response.id)

    toast({
      description: 'Essay submitted successfully. Processing...',
    })
  } catch (err) {
    console.error('Error submitting essay:', err)
    if (err instanceof AxiosError && err.response?.status === 429) {
      toast({
        description: 'You have reached the maximum number of requests. Please try again later.',
        variant: 'destructive',
      })
    } else {
      toast({
        description: 'Failed to submit essay',
        variant: 'destructive',
      })
    }
  } finally {
    isLoading.value = false
  }
}

// Clean up polling when component is unmounted
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
})
</script>
