<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const email = ref('');
const password = ref('');
const error = ref('');
const emailError = ref('');
const passwordError = ref('');

const authStore = useAuthStore();
const router = useRouter();

const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const validatePassword = (password: string): boolean => {
  return password.length >= 8 && /\d/.test(password);
};

watch(email, (newValue) => {
  if (!validateEmail(newValue)) {
    emailError.value = 'Invalid email address.';
  } else {
    emailError.value = '';
  }
});

watch(password, (newValue) => {
  if (!validatePassword(newValue)) {
    passwordError.value = 'Password must be at least 8 characters long and contain a number.';
  } else {
    passwordError.value = '';
  }
});

const resetError = () => {
  error.value = '';
};

const login = async () => {
  if (emailError.value || passwordError.value) {
    error.value = 'Please fix the errors before submitting.';
    return;
  }
  await authStore.login(email.value, password.value, router);
  if (!authStore.isAuthenticated) {
    error.value = 'Login failed. Please check your credentials.';
  }
};
</script>

<template>
  <Card class="mx-auto max-w-sm mt-20">
    <CardHeader>
      <CardTitle class="text-2xl">
        Login
      </CardTitle>
      <CardDescription>
        Enter your email below to login to your account
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid gap-4">
        <div class="grid gap-2">
          <Label for="email">Email</Label>
          <Input id="email" type="email" v-model="email" placeholder="name@example.com" required />
          <p v-if="emailError" class="text-error-foreground">{{ emailError }}</p>
        </div>
        <div class="grid gap-2">
          <div class="flex items-center">
            <Label for="password">Password</Label>
            <router-link :to="{ name: 'forgot-password'}" class="ml-auto inline-block text-sm underline">
              Forgot your password?
            </router-link>
          </div>
          <Input id="password" type="password" v-model="password" required @input="resetError" />
          <p v-if="passwordError" class="text-error-foreground">{{ passwordError }}</p>
        </div>
        <Button type="submit" class="w-full" @click="login">
          Login
        </Button>
      </div>
      <div class="mt-4 text-center text-sm">
        Don't have an account?
        <router-link :to="{ name: 'signup' }" class="underline">
          Sign up
        </router-link>
      </div>
    </CardContent>
  </Card>
</template>
