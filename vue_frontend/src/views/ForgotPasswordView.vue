<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">Forgot Password</CardTitle>
      <CardDescription>
        Enter your email address and we'll send you a link to reset your password
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid gap-4">
        <div class="grid gap-2">
          <Label for="email">Email</Label>
          <Input id="email" type="email" v-model="email" placeholder="name@example.com" required />
          <p v-if="emailError" class="text-error-foreground text-sm break-words">
            {{ emailError }}
          </p>
        </div>

        <p v-if="error" class="text-error-foreground text-sm text-center break-words">
          {{ error }}
        </p>

        <Button
          type="submit"
          class="w-full"
          @click="handleSubmit"
          :disabled="isSubmitting || !isFormValid"
        >
          {{ isSubmitting ? 'Sending...' : 'Send Reset Link' }}
        </Button>

        <div class="mt-4 text-center text-sm">
          Remember your password?
          <router-link :to="{ name: 'login' }" class="underline"> Back to login </router-link>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AuthService } from '@/services/authService'

const email = ref('')
const error = ref('')
const emailError = ref('')
const isSubmitting = ref(false)
const router = useRouter()

const validateEmail = (email: string): boolean => {
  if (!email.trim()) return false
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

watch(email, (newValue) => {
  if (!newValue.trim()) {
    emailError.value = 'Email is required.'
  } else if (!validateEmail(newValue)) {
    emailError.value = 'Invalid email address.'
  } else {
    emailError.value = ''
  }
})

const isFormValid = computed(() => {
  return email.value.trim() && !emailError.value
})

const handleSubmit = async () => {
  if (!email.value.trim()) {
    emailError.value = 'Email is required.'
    return
  }

  if (!validateEmail(email.value)) {
    emailError.value = 'Invalid email address.'
    return
  }

  isSubmitting.value = true
  try {
    await AuthService.passwordReset(email.value)
    router.push({ name: 'password-reset-sent' })
  } catch (err) {
    error.value = 'Failed to send reset email. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
