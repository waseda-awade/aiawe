<template>
    <div>
      <h2>Register</h2>
      <form @submit.prevent="register" >
        <div>
          <label for="email">Email:</label>
          <input v-model="email" id="email" type="email" required>
        </div>
        <div>
          <label for="password">Password:</label>
          <input v-model="password" id="password" type="password" required>
        </div>
        <button type="submit">Register</button>
      </form>
      <p v-if="error">{{ error }}</p>
      <p v-if="success">{{ success }}</p>
    </div>
  </template>

  <script>

  import api from '@/services/api'

  export default {
    data() {
      return {
        email: '',
        password: '',
        error: '',
        success: ''
      }
    },
    methods: {
      async register() {
        try {
          const response = await api.post('/api/register', {
              email: this.email,
              password: this.password
            })
          const data = await response.json()
          if (response.ok) {
            this.success = 'Registration successful! Please log in.'
            setTimeout(() => {
              this.$router.push('/login')
            }, 1000)
          } else {
            this.error = data.error || 'Registration failed'
          }
        } catch (err) {
          this.error = 'An error occurred during registration: ' + err
        }
      }
    }
  }
  </script>
