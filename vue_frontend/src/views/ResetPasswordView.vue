<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">Reset Password</CardTitle>
      <CardDescription> Enter your new password below </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid gap-4">
        <div class="grid gap-2">
          <Label for="password">New Password</Label>
          <Input
            id="password"
            type="password"
            v-model="password"
            placeholder="Enter your new password"
            required
          />
          <p v-if="passwordError" class="text-error-foreground text-sm break-words">
            {{ passwordError }}
          </p>
        </div>

        <div class="grid gap-2">
          <Label for="confirm-password">Confirm Password</Label>
          <Input
            id="confirm-password"
            type="password"
            v-model="confirmPassword"
            placeholder="Confirm your new password"
            required
          />
          <p v-if="confirmPasswordError" class="text-error-foreground text-sm break-words">
            {{ confirmPasswordError }}
          </p>
        </div>

        <p v-if="error" class="text-error-foreground text-sm text-center break-words">
          {{ error }}
        </p>

        <Button
          type="submit"
          class="w-full"
          @click="handleSubmit"
          :disabled="isSubmitting || !isFormValid || success"
        >
          {{ isSubmitting ? 'Resetting...' : 'Reset Password' }}
        </Button>
        <p v-if="success" class="text-success-foreground text-sm text-center break-words">
          Password reset successful. Redirecting to
          <router-link :to="{ name: 'login' }" class="underline">login</router-link>
          ...
        </p>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AuthService, isAuthError } from '@/services/authService'

const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')
const isSubmitting = ref(false)
const success = ref(false)

const router = useRouter()
const route = useRoute()

const validatePassword = (password: string): boolean => {
  return password.length >= 8 && /\d/.test(password)
}

const validateConfirmPassword = (password: string, confirmPassword: string): boolean => {
  if (!confirmPassword.trim()) {
    return false
  }
  return password === confirmPassword
}

watch(password, (newValue) => {
  if (!newValue.trim()) {
    passwordError.value = 'Password is required.'
  } else if (!validatePassword(newValue)) {
    passwordError.value =
      'Password must be at least 8 characters and contain uppercase, lowercase, and numbers.'
  } else {
    passwordError.value = ''
  }

  if (confirmPassword.value && !validateConfirmPassword(newValue, confirmPassword.value)) {
    confirmPasswordError.value = 'Passwords do not match.'
  } else {
    confirmPasswordError.value = ''
  }
})

watch(confirmPassword, (newValue) => {
  if (!newValue.trim()) {
    confirmPasswordError.value = 'Confirm password is required.'
  } else if (!validateConfirmPassword(password.value, newValue)) {
    confirmPasswordError.value = 'Passwords do not match.'
  } else {
    confirmPasswordError.value = ''
  }
})

const isFormValid = computed(() => {
  return (
    password.value.trim() &&
    confirmPassword.value.trim() &&
    !passwordError.value &&
    !confirmPasswordError.value
  )
})

const handleSubmit = async () => {
  // Reset errors
  passwordError.value = ''
  confirmPasswordError.value = ''
  error.value = ''

  // Validate password
  if (!validatePassword(password.value)) {
    passwordError.value = 'Password must be at least 8 characters long and contain a number.'
    return
  }

  // Validate password confirmation
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Passwords do not match.'
    return
  }

  isSubmitting.value = true
  try {
    await AuthService.passwordResetConfirm(
      route.params.uid as string,
      route.params.token as string,
      password.value
    )
    success.value = true
    // Navigate to the login page after 3 seconds
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 3000)
  } catch (err) {
    if (isAuthError(err)) {
      console.error(err.field === 'token')
      if (err.field === 'token') {
        error.value = 'Invalid token. Please request a new password reset.'
      } else {
        error.value = 'Failed to reset password. Please try again.'
      }
    } else {
      error.value = 'Unknown error. Please try again.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
