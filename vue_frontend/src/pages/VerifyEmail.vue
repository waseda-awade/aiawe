<!-- vue_frontend/src/pages/VerifyEmail.vue -->
<template>
    <div>
        <h2>Email Verification</h2>
        <form @submit.prevent="verifyEmail">
            <div>
                <label for="verification-code">Verification Code:</label>
                <input v-model="verificationCode" id="verification-code" type="text" required>
            </div>
            <button type="submit">Verify</button>
        </form>
        <p v-if="message">{{ message }}</p>
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
            verificationCode: '',
            message: '',
            countdown: 3
        }
    },
    methods: {
        async verifyEmail() {
            if (!this.verificationCode) {
                this.message = 'Please enter a verification code.'
                return
            }

            try {
                const response = await this.authStore.verifyEmail(this.verificationCode)

                if (response?.status === 200) {
                    this.message = `Email verification successful! Redirecting to login in ${this.countdown} seconds...`
                    const countdownInterval = setInterval(() => {
                        this.countdown -= 1
                        this.message = `Email verification successful! Redirecting to login in ${this.countdown} seconds...`
                        if (this.countdown === 0) {
                            clearInterval(countdownInterval)
                        }
                    }, 1000)
                    setTimeout(() => {
                        this.$router.push({ name: 'login' })
                    }, 3000)
                } else {
                    this.message = 'Email verification failed.'
                }
            } catch (err) {
                this.message = 'An error occurred during email verification: ' + err
            }
        }
    }
}
</script>
