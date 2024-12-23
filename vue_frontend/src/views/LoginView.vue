<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
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
const route = useRoute();

const validateEmail = (email: string): boolean => {
  if (!email.trim()) {
    return false;
  }
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const validatePassword = (password: string): boolean => {
  if (!password.trim()) {
    return false;
  }
  return password.length >= 8 && /\d/.test(password);
};

watch(email, (newValue) => {
  if (!newValue.trim()) {
    emailError.value = 'Email is required.';
  } else if (!validateEmail(newValue)) {
    emailError.value = 'Invalid email address.';
  } else {
    emailError.value = '';
  }
});

watch(password, (newValue) => {
  if (!newValue.trim()) {
    passwordError.value = 'Password is required.';
  } else if (!validatePassword(newValue)) {
    passwordError.value = 'Password must be at least 8 characters long and contain a number.';
  } else {
    passwordError.value = '';
  }
});

const resetError = () => {
  error.value = '';
};

const login = async () => {
  // Check for empty fields first
  if (!email.value.trim() || !password.value.trim()) {
    error.value = 'All fields are required.';
    return;
  }

  if (emailError.value || passwordError.value) {
    error.value = 'Please fix the errors before submitting.';
    return;
  }

  await authStore.login(email.value, password.value);
  if (!authStore.isAuthenticated) {
    error.value = 'Login failed. Please check your credentials.';
  } else {
    // Get the redirect path from query or default to dashboard
    const redirectPath = typeof route.query.redirect === 'string'
      ? route.query.redirect
      : { name: 'dashboard' };
    router.push(redirectPath);
  }
};
</script>

<template>
  <Card class="mx-auto w-96 mt-20">
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
          <p v-if="emailError" class="text-error-foreground text-sm break-words">{{ emailError }}</p>
        </div>
        <div class="grid gap-2">
          <div class="flex items-center">
            <Label for="password">Password</Label>
            <router-link :to="{ name: 'forgot-password'}" class="ml-auto inline-block text-sm underline">
              Forgot your password?
            </router-link>
          </div>
          <Input id="password" type="password" v-model="password" placeholder="Enter your password" required @input="resetError" />
          <p v-if="passwordError" class="text-error-foreground text-sm break-words">{{ passwordError }}</p>
        </div>

        <p v-if="error" class="text-error-foreground text-sm text-center break-words">{{ error }}</p>

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
