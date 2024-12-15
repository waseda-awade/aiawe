import {createRouter, createWebHistory} from 'vue-router'
import Home from './pages/Home.vue'
import Login from './pages/Login.vue'
import Register from "./pages/Register.vue";

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
        component: () => import('./pages/VerifyEmail.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
