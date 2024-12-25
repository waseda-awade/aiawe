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
            :disabled="isProcessing"
            :class="{ 'border-destructive': isOverLimit }"
          />
          <div class="flex justify-end items-center text-sm">
            <p class="text-muted-foreground" :class="{ 'text-destructive': isOverLimit }">
              {{ charCount }}/{{ MAX_CHARS }}
            </p>
          </div>
        </div>

        <p v-if="error" class="text-destructive text-sm">{{ error }}</p>

        <Button
          class="w-full"
          @click="handleSubmit"
          :disabled="isLoading || isProcessing || !content.trim() || isOverLimit"
        >
          <Loader2 v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
          {{ isLoading ? 'Submitting...' : 'Submit' }}
        </Button>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Loader2 } from 'lucide-vue-next'
import FileUpload from '@/components/FileUpload.vue'
import { useDocumentProcessor } from '@/composables/useDocumentProcessor'
import { useToast } from '@/components/ui/toast/use-toast'

const MAX_CHARS = 5000
const content = ref('')
const isLoading = ref(false)
const error = ref('')

const { toast } = useToast()
const { processDocument, isProcessing } = useDocumentProcessor()

const charCount = computed(() => content.value.length)
const remainingChars = computed(() => MAX_CHARS - charCount.value)
const isOverLimit = computed(() => charCount.value > MAX_CHARS)

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
    // TODO: Replace with your actual API endpoint
    await fetch('/api/submit-text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: content.value }),
    })
    // Optional: Show success message or clear the form
    content.value = ''
  } catch (err) {
    error.value = 'Failed to submit text. Please try again.'
    console.error('Error submitting text:', err)
  } finally {
    isLoading.value = false
  }
}
</script>
