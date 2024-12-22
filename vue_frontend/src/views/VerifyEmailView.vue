<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const verificationCode = ref('');
const message = ref('');
const countdown = ref(3);
const codeError = ref('');

const authStore = useAuthStore();
const router = useRouter();

const validateCode = (code: string): boolean => {
  return code.trim().length > 0;
};

const resetError = () => {
  message.value = '';
  codeError.value = '';
};

const verifyEmail = async () => {
  resetError();

  if (!validateCode(verificationCode.value)) {
    codeError.value = 'Please enter a verification code.';
    return;
  }

  try {
    const response = await authStore.verifyEmail(verificationCode.value);

    if (response?.status === 200) {
      message.value = `Email verification successful! Redirecting to login in ${countdown.value} seconds...`;

      const countdownInterval = setInterval(() => {
        countdown.value -= 1;
        message.value = `Email verification successful! Redirecting to login in ${countdown.value} seconds...`;

        if (countdown.value === 0) {
          clearInterval(countdownInterval);
        }
      }, 1000);

      setTimeout(() => {
        router.push({ name: 'login' });
      }, 3000);
    } else {
      message.value = 'Email verification failed.';
    }
  } catch (err) {
    message.value = 'An error occurred during email verification: ' + err;
  }
};
</script>

<template>
  <Card class="mx-auto w-96 mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">
        Email Verification
      </CardTitle>
      <CardDescription>
        Please enter the verification code sent to your email
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid gap-4">
        <div class="grid gap-2">
          <Label for="verification-code">Verification Code</Label>
          <Input
            id="verification-code"
            type="text"
            v-model="verificationCode"
            placeholder="Enter verification code"
            required
            @input="resetError"
          />
          <p v-if="codeError" class="text-error-foreground text-sm break-words">{{ codeError }}</p>
        </div>

        <p v-if="message"
           :class="{
             'text-success-foreground': message.includes('successful'),
             'text-error-foreground': !message.includes('successful'),
             'text-sm text-center break-words': true
           }"
        >
          {{ message }}
        </p>

        <Button type="submit" class="w-full" @click="verifyEmail">
          Verify Email
        </Button>
      </div>
      <div class="mt-4 text-center text-sm">
        <router-link :to="{ name: 'login' }" class="underline">
          Back to Login
        </router-link>
      </div>
    </CardContent>
  </Card>
</template>
