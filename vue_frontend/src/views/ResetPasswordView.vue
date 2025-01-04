<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">Reset Password</CardTitle>
      <CardDescription>Enter your new password below</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit="handleSubmit" class="grid gap-4">
        <FormField
          v-slot="{ componentField }"
          name="password"
        >
          <FormItem>
            <FormLabel>New Password</FormLabel>
            <FormControl>
              <Input
                v-bind="componentField"
                type="password"
                placeholder="Enter your new password"
                :disabled="isSubmitting || success"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField
          v-slot="{ componentField }"
          name="confirmPassword"
        >
          <FormItem>
            <FormLabel>Confirm Password</FormLabel>
            <FormControl>
              <Input
                v-bind="componentField"
                type="password"
                placeholder="Confirm your new password"
                :disabled="isSubmitting || success"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <div v-if="generalError" class="text-destructive text-sm text-center">
          {{ generalError }}
        </div>

        <Button
          type="submit"
          class="w-full"
          :disabled="isSubmitting || !form.meta.value.valid || success"
        >
          {{ isSubmitting ? 'Resetting...' : 'Reset Password' }}
        </Button>

        <p v-if="success" class="text-success-foreground text-sm text-center">
          Password reset successful. Redirecting to
          <router-link :to="{ name: 'login' }" class="underline">login</router-link>
          ...
        </p>
      </form>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { AuthService, isAuthError } from '@/services/authService'
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
import { resetPasswordFormSchema } from '@/lib/validations'

const router = useRouter()
const route = useRoute()
const isSubmitting = ref(false)
const generalError = ref<string | null>(null)
const success = ref(false)

const form = useForm({
  validationSchema: toTypedSchema(resetPasswordFormSchema),
  initialValues: {
    password: '',
    confirmPassword: '',
  },
})

const handleSubmit = form.handleSubmit(async (values) => {
  isSubmitting.value = true
  generalError.value = null

  try {
    await AuthService.passwordResetConfirm(
      route.params.uid as string,
      route.params.token as string,
      values.password
    )
    success.value = true
    // Navigate to the login page after 3 seconds
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 3000)
  } catch (err) {
    if (isAuthError(err)) {
      if (err.field === 'token') {
        generalError.value = 'Invalid token. Please request a new password reset.'
      } else if (err.field === 'password') {
        form.setFieldError('password', err.message)
      } else {
        generalError.value = 'Failed to reset password. Please try again.'
      }
    } else {
      generalError.value = 'Unknown error. Please try again.'
    }
  } finally {
    isSubmitting.value = false
  }
})
</script>
