import { defineStore } from 'pinia'
import type { AxiosResponse } from 'axios';
import type { Router } from 'vue-router';
import api from '@/services/api'; // Assuming api is exported from this path

interface AuthState {
    user: any;
    isAuthenticated: boolean;
    saveState: () => void;
}

export const useAuthStore = defineStore('auth', {
    state: () => {
        const storedState = localStorage.getItem('authState')
        return storedState ? JSON.parse(storedState) : {
            user: null,
            isAuthenticated: false
        }
    },
    actions: {

        async login(email: string, password: string, router: Router | null = null) {
            const response = await api.post(`/dj-rest-auth/login/`, { email, password })
            const data = response.data
            if (data.user) {
                this.isAuthenticated = true
                this.user = data.user
                this.saveState()
                if (router){
                    await router.push({name: "home"})
                }
            } else {
                this.user = null
                this.isAuthenticated = false
                this.saveState()
            }
        },

        async logout(router: Router | null = null): Promise<void> {
            try {
                const response: AxiosResponse = await api.post(`/dj-rest-auth/logout/`);
                if (response.status === 200) {
                    this.user = null
                    this.isAuthenticated = false
                    this.saveState()
                    if (router){
                        await router.push({name: "login"})
                    }
                }
            } catch (error) {
                console.error('Logout failed', error)
                throw error
            }
        },

        async register(email: string, password: string, router: Router | null = null): Promise<void> {
            try {
                const response: AxiosResponse = await api.post(`/dj-rest-auth/registration/`, { email, password1: password, password2: password });
                if (response.status === 201) {
                    if (router) {
                        await router.push({ name: "verify-email" });
                    }
                }
            } catch (error) {
                console.error('Registration failed', error);
                throw error;
            }
        },

        async verifyEmail(key: string, router: Router | null = null): Promise<AxiosResponse> {
            try {
                const response: AxiosResponse = await api.post(`/dj-rest-auth/registration/verify-email/`, { key });
                console.log({ response });
                if (response?.status === 200) {
                    if (router) {
                        await router.push({ name: "login" });
                    }
                }
                return response;
            } catch (error) {
                console.error('Verify email failed', error);
                throw error;
            }
        },

        async fetchUser() {
            try {
                const response = await api.get(`/dj-rest-auth/user/`)
                if (response.status === 200) {
                    const data = response.data
                    console.log({data})
                    this.user = data
                    this.isAuthenticated = true
                }
                else{
                    this.user = null
                    this.isAuthenticated = false
                }
            } catch (error) {
                console.error('Fetch user failed', error)
                this.user = null
                this.isAuthenticated = false
            }
        },

        saveState() {
            /*
            We save state to local storage to keep the
            state when the user reloads the page.

            This is a simple way to persist state. For a more robust solution,
            use pinia-persistent-state.
             */
            localStorage.setItem('authState', JSON.stringify({
                user: this.user,
                isAuthenticated: this.isAuthenticated
            }))
        }
    }
})
