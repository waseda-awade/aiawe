<template>
  <div class="container mx-auto mt-20">
    <div class="login-form">
      <h1 class="text-3xl font-bold mb-6">Login Page</h1>
      <form @submit.prevent="login" class="space-y-4">
        <div class="mb-3">
          <label for="email" class="block text-lg font-medium">Email:</label>
          <input v-model="email" id="email" class="w-full border border-gray-300 rounded px-3 py-2"  type="text" placeholder="Your Email" required @input="resetError">
          <p v-if="emailError" class="error">{{ emailError }}</p>
        </div>
        <div class="mb-3">
          <label for="password" class="block text-lg font-medium">Password:</label>
          <input v-model="password" id="password" class="w-full border border-gray-300 rounded px-3 py-2"  type="password" placeholder="Your password"
            required @input="resetError">
          <small class="form-text text-muted">Password must be at least 8 characters long and contain a number.</small>
          <p v-if="passwordError" class="error">{{ passwordError }}</p>
        </div>
        <button type="submit" class="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600">Login</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <p><a href="/register">Register</a> | <a href="/forgot-password">Forgot Password?</a></p>
    </div>
  </div>
</template>

<style scoped>
/* .login-form {
  max-width: 400px;
  margin: 0 auto;
} */

.error {
  color: red;
}
</style>

<script>
import { useAuthStore } from '@/store/auth'

export default {
  setup() {
    const authStore = useAuthStore()
    return {
      authStore
    }
  },
  data() {
    return {
      email: "",
      password: "",
      error: "",
      emailError: "",
      passwordError: ""
    }
  },
  watch: {
    email(value) {
      if (!this.validateEmail(value)) {
        this.emailError = 'Invalid email address.'
      } else {
        this.emailError = ''
      }
    },
    password(value) {
      if (!this.validatePassword(value)) {
        this.passwordError = 'Password must be at least 8 characters long and contain a number.'
      } else {
        this.passwordError = ''
      }
    }
  },
  methods: {
    async login() {
      if (this.emailError || this.passwordError) {
        this.error = 'Please fix the errors before submitting.'
        return
      }
      await this.authStore.login(this.email, this.password, this.$router)
      if (!this.authStore.isAuthenticated) {
        this.error = 'Login failed. Please check your credentials.'
      }
    },
    resetError() {
      this.error = ""
    },
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    validatePassword(password) {
      return password.length >= 8 && /\d/.test(password)
    }
  }
}
</script>
