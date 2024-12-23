<script setup lang="ts">
import NavBar from '@/components/NavBar.vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const router = useRouter();

// Redirect authenticated users away from auth pages
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'dashboard' });
  }
});
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <!-- NavBar (simplified version) -->
    <nav class="w-full py-4 border-b">
      <div class="container mx-auto px-4">
        <router-link :to="{ name: 'home' }" class="flex items-center justify-center">
          <!-- Replace with your actual logo -->
          <span class="text-2xl font-bold text-primary">AWE</span>
        </router-link>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow flex items-start justify-center px-4 py-8">
      <div class="w-full">
        <router-view v-slot="{ Component }">
          <transition
            name="fade"
            mode="out-in"
            appear
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-6 border-t">
      <div class="container mx-auto px-4">
        <div class="text-center text-sm text-muted-foreground">
          <p>&copy; {{ new Date().getFullYear() }} Your Company. All rights reserved.</p>
          <div class="mt-2 space-x-4">
            <router-link :to="{ name: 'home' }" class="hover:text-primary transition-colors">
              Terms of Service
            </router-link>
            <router-link :to="{ name: 'home' }" class="hover:text-primary transition-colors">
              Privacy Policy
            </router-link>
            <a href="mailto:support@yourcompany.com" class="hover:text-primary transition-colors">
              Support
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
