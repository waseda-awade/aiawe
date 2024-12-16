import {createRouter, createWebHistory} from 'vue-router'
import Home from '@/views/HomeView.vue'
import Login from '@/views/LoginView.vue'
import Register from "@/views/RegisterView.vue";

const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
        path: '/register',
        name: 'register',
        component: Register
    },
    {
        path: '/verify-email',
        name: 'verify-email',
        component: () => import('@/views/VerifyEmailView.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
