<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'

const name = ref('name')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const nameError = ref('')
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

const authStore = useAuthStore()
const { loading } = storeToRefs(authStore)
const router = useRouter()

const validateName = (name: string): boolean => {
  return name.length >= 2
}

const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const validatePassword = (password: string): boolean => {
  if (!password.trim()) {
    return false
  }
  return (
    password.length >= 8 && /\d/.test(password) && /[A-Z]/.test(password) && /[a-z]/.test(password)
  )
}

const validateConfirmPassword = (password: string, confirmPassword: string): boolean => {
  if (!confirmPassword.trim()) {
    return false
  }
  return password === confirmPassword
}

watch(name, (newValue) => {
  if (!validateName(newValue)) {
    nameError.value = 'Name must be at least 2 characters long.'
  } else {
    nameError.value = ''
  }
})

watch(email, (newValue) => {
  if (!validateEmail(newValue)) {
    emailError.value = 'Invalid email address.'
  } else {
    emailError.value = ''
  }
})

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

const resetError = () => {
  error.value = ''
}

const isFormValid = computed(() => {
  return (
    email.value.trim() &&
    password.value.trim() &&
    confirmPassword.value.trim() &&
    !emailError.value &&
    !passwordError.value &&
    !confirmPasswordError.value
  )
})

const signup = async () => {
  // Check for empty fields first
  if (!email.value.trim() || !password.value.trim() || !confirmPassword.value.trim()) {
    error.value = 'All fields are required.'
    return
  }

  if (emailError.value || passwordError.value || confirmPasswordError.value) {
    error.value = 'Please fix the errors before submitting.'
    return
  }

  if (!validateConfirmPassword(password.value, confirmPassword.value)) {
    error.value = 'Passwords do not match.'
    return
  }

  try {
    await authStore.signup(email.value, password.value, router)
  } catch (err: any) {
    console.error('Signup failed:', err)

    // Clear previous field-specific errors
    emailError.value = ''
    passwordError.value = ''

    if (err.field) {
      // Handle field-specific errors
      switch (err.field) {
        case 'email':
          emailError.value = err.message
          break
        case 'password1':
        case 'password2':
          passwordError.value = err.message
          break
        default:
          error.value = err.message
      }
    } else if (err.code === 'NETWORK_ERROR') {
      error.value = 'Network error. Please try again.'
    } else {
      // General error
      error.value = err.message || 'Signup failed. Please try again.'
    }

    // If there are multiple field errors, you can handle them all
    if (err.details) {
      Object.entries(err.details).forEach(([field, messages]) => {
        if (field === 'email') {
          emailError.value = messages[0]
        } else if (field === 'password1' || field === 'password2') {
          passwordError.value = messages[0]
        }
      })
    }
  }
}
</script>

<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl"> Create an Account </CardTitle>
      <CardDescription> Enter your details below to create your account </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid gap-4">
        <!-- <div class="grid gap-2">
          <Label for="name">Full Name</Label>
          <Input
            id="name"
            type="text"
            v-model="name"
            placeholder="John Doe"
            required
            :disabled="loading"
          />
          <p v-if="nameError" class="text-error-foreground text-sm break-words">{{ nameError }}</p>
        </div> -->

        <div class="grid gap-2">
          <Label for="email">Email</Label>
          <Input
            id="email"
            type="email"
            v-model="email"
            placeholder="name@example.com"
            required
            :disabled="loading"
          />
          <p v-if="emailError" class="text-error-foreground text-sm break-words">
            {{ emailError }}
          </p>
        </div>

        <div class="grid gap-2">
          <Label for="password">Password</Label>
          <Input
            id="password"
            type="password"
            v-model="password"
            placeholder="Create a password"
            required
            @input="resetError"
            :disabled="loading"
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
            placeholder="Confirm your password"
            required
            @input="resetError"
            :disabled="loading"
          />
          <p v-if="confirmPasswordError" class="text-error-foreground text-sm break-words">
            {{ confirmPasswordError }}
          </p>
        </div>

        <p v-if="error" class="text-error-foreground text-sm text-center break-words">
          {{ error }}
        </p>

        <Button type="submit" class="w-full" @click="signup" :disabled="loading || !isFormValid">
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          {{ loading ? 'Creating account...' : 'Sign Up' }}
        </Button>
      </div>
      <div class="mt-4 text-center text-sm">
        Already have an account?
        <router-link :to="{ name: 'login' }" class="underline" :tabindex="loading ? -1 : 0">
          Login
        </router-link>
      </div>
    </CardContent>
  </Card>
</template>
