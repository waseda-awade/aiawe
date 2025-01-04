<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">Change Password</CardTitle>
      <CardDescription>Enter your current password and a new password</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit="handleSubmit" class="grid gap-4">
        <FormField
          v-slot="{ componentField }"
          name="currentPassword"
        >
          <FormItem>
            <FormLabel>Current Password</FormLabel>
            <FormControl>
              <Input
                v-bind="componentField"
                type="password"
                placeholder="Enter your current password"
                :disabled="isSubmitting || success"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField
          v-slot="{ componentField }"
          name="newPassword"
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
            <FormLabel>Confirm New Password</FormLabel>
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
          {{ isSubmitting ? 'Changing...' : 'Change Password' }}
        </Button>

        <p v-if="success" class="text-success-foreground text-sm text-center">
          Password changed successfully!
        </p>
      </form>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
import { useToast } from '@/components/ui/toast/use-toast'
import { changePasswordFormSchema } from '@/lib/validations'

const isSubmitting = ref(false)
const generalError = ref<string | null>(null)
const success = ref(false)
const { toast } = useToast()

const form = useForm({
  validationSchema: toTypedSchema(changePasswordFormSchema),
  initialValues: {
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  },
})

const handleSubmit = form.handleSubmit(async (values) => {
  isSubmitting.value = true
  generalError.value = null

  try {
    await AuthService.changePassword(values.currentPassword, values.newPassword)
    success.value = true
    toast({
      title: 'Success',
      description: 'Your password has been changed successfully.',
    })
  } catch (err) {
    if (isAuthError(err)) {
      if (err.field === 'old_password') {
        form.setFieldError('currentPassword', 'Current password is incorrect.')
      } else if (err.field === 'new_password') {
        form.setFieldError('newPassword', err.message)
      } else {
        generalError.value = err.message || 'Failed to change password. Please try again.'
      }
    } else {
      generalError.value = 'Unknown error. Please try again.'
    }
  } finally {
    isSubmitting.value = false
  }
})
</script>
