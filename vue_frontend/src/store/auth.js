import { defineStore } from 'pinia'
import api from '../services/api'


export const useAuthStore = defineStore('auth', {
    state: () => {
        const storedState = localStorage.getItem('authState')
        return storedState ? JSON.parse(storedState) : {
            user: null,
            isAuthenticated: false
        }
    },
    actions: {

        async login(username, password, router=null) {
            const response = await api.post(`/dj-rest-auth/login/`, { username, password })
            const data = response.data
            if (data.key) {
                this.isAuthenticated = true
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

        async logout(router=null) {
            try {
                const response = await api.post(`/dj-rest-auth/logout/`)
                console.log({response})
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
