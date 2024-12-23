import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/BaseLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: HomeView,
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/auth',
    name: 'auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: {
      requiresGuest: true
    },
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
      },
      {
        path: 'signup',
        name: 'signup',
        component: () => import('@/views/SignupView.vue'),
      },
      {
        path: 'verify-email',
        name: 'verify-email',
        component: () => import('@/views/VerifyEmailView.vue'),
      },
      // Password Reset Flow
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: () => import('@/views/ForgotPasswordView.vue'),
      },
      {
        path: 'reset-password/:uid/:token',
        name: 'reset-password',
        component: () => import('@/views/ResetPasswordView.vue'),
      },
      {
        path: 'password-reset-success',
        name: 'password-reset-success',
        component: () => import('@/views/PasswordResetSuccessView.vue'),
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from) => {
  const authStore = useAuthStore()

  // Check if the route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  // Check if the route requires guest access
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  // If the route requires authentication and user is not authenticated
  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login page with the intended destination
    return {
      name: 'login',
      query: { redirect: to.fullPath }
    }
  }

  // If the route requires guest access and user is authenticated
  if (requiresGuest && authStore.isAuthenticated) {
    // Redirect to dashboard or home
    return {
      name: 'dashboard'
    }
  }
})

export default router
