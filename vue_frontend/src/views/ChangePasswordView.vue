<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">Change Password</CardTitle>
      <CardDescription> Enter your current password and a new password </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid gap-4">
        <div class="grid gap-2">
          <Label for="current-password">Current Password</Label>
          <Input
            id="current-password"
            type="password"
            v-model="currentPassword"
            placeholder="Enter your current password"
            required
          />
          <p v-if="currentPasswordError" class="text-error-foreground text-sm break-words">
            {{ currentPasswordError }}
          </p>
        </div>

        <div class="grid gap-2">
          <Label for="new-password">New Password</Label>
          <Input
            id="new-password"
            type="password"
            v-model="newPassword"
            placeholder="Enter your new password"
            required
          />
          <p v-if="newPasswordError" class="text-error-foreground text-sm break-words">
            {{ newPasswordError }}
          </p>
        </div>

        <div class="grid gap-2">
          <Label for="confirm-password">Confirm New Password</Label>
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
          {{ isSubmitting ? 'Changing...' : 'Change Password' }}
        </Button>
        <p v-if="success" class="text-success-foreground text-sm text-center break-words">
          Password changed successfully!
        </p>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AuthService, isAuthError } from '@/services/authService'
import { useToast } from '@/components/ui/toast/use-toast'

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const currentPasswordError = ref('')
const newPasswordError = ref('')
const confirmPasswordError = ref('')
const isSubmitting = ref(false)
const success = ref(false)
const { toast } = useToast()

const validatePassword = (password: string): boolean => {
  return password.length >= 8 && /\d/.test(password)
}

const validateConfirmPassword = (password: string, confirmPassword: string): boolean => {
  if (!confirmPassword.trim()) {
    return false
  }
  return password === confirmPassword
}

watch(newPassword, (newValue) => {
  if (!newValue.trim()) {
    newPasswordError.value = 'New password is required.'
  } else if (!validatePassword(newValue)) {
    newPasswordError.value =
      'Password must be at least 8 characters and contain uppercase, lowercase, and numbers.'
  } else {
    newPasswordError.value = ''
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
  } else if (!validateConfirmPassword(newPassword.value, newValue)) {
    confirmPasswordError.value = 'Passwords do not match.'
  } else {
    confirmPasswordError.value = ''
  }
})

const isFormValid = computed(() => {
  return (
    currentPassword.value.trim() &&
    newPassword.value.trim() &&
    confirmPassword.value.trim() &&
    !newPasswordError.value &&
    !confirmPasswordError.value
  )
})

const handleSubmit = async () => {
  // Reset errors
  currentPasswordError.value = ''
  newPasswordError.value = ''
  confirmPasswordError.value = ''
  error.value = ''

  // Validate new password
  if (!validatePassword(newPassword.value)) {
    newPasswordError.value = 'Password must be at least 8 characters long and contain a number.'
    return
  }

  // Validate password confirmation
  if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Passwords do not match.'
    return
  }

  isSubmitting.value = true
  try {
    await AuthService.changePassword(currentPassword.value, newPassword.value)
    success.value = true
    toast({
      title: 'Success',
      description: 'Your password has been changed successfully.',
    })
  } catch (err) {
    if (isAuthError(err)) {
      if (err.field === 'old_password') {
        currentPasswordError.value = 'Current password is incorrect.'
      } else {
        error.value = err.message || 'Failed to change password. Please try again.'
      }
    } else {
      error.value = 'Unknown error. Please try again.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
