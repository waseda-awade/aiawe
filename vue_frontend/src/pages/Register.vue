<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div>
        <label for="email">Email:</label>
        <input v-model="email" id="email" type="email" required>
      </div>
      <div>
        <label for="password1">Password:</label>
        <input v-model="password1" id="password1" type="password" required>
      </div>
      <div>
        <label for="password2">Confirm Password:</label>
        <input v-model="password2" id="password2" type="password" required>
      </div>
      <button type="submit">Register</button>
    </form>
    <p v-if="error">{{ error }}</p>
    <p v-if="success">{{ success }}</p>
  </div>
</template>

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
      email: '',
      password1: '',
      password2: '',
      error: '',
      success: ''
    }
  },
  methods: {
    async register() {
      if (this.password1 !== this.password2) {
        this.error = 'Passwords do not match.'
        return
      }
      try {
        await this.authStore.register(this.email, this.password1, this.$router)
        this.success = 'Registration successful! Please check your email for verification.'
      } catch (err) {
        this.error = 'An error occurred during registration: ' + err
      }
    }
  }
}
</script>
