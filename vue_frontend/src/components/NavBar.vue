<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const username = computed(() => authStore.user?.username || '');
const logout = () => {
  authStore.logout();
};
</script>

<template>
  <NavigationMenu>
    <NavigationMenuList>
      <NavigationMenuItem>
        <NavigationMenuLink href="/" :class="navigationMenuTriggerStyle()">
          Home
        </NavigationMenuLink>
      </NavigationMenuItem>
      <NavigationMenuItem v-if="!isAuthenticated">
        <NavigationMenuLink href="/login" :class="navigationMenuTriggerStyle()">
          Login
        </NavigationMenuLink>
      </NavigationMenuItem>
      <NavigationMenuItem v-if="!isAuthenticated">
        <NavigationMenuLink href="/signup" :class="navigationMenuTriggerStyle()">
          Sign up
        </NavigationMenuLink>
      </NavigationMenuItem>
      <NavigationMenuItem v-else>
        <NavigationMenuLink href="/profile" :class="navigationMenuTriggerStyle()">
          Welcome, {{ username }}
        </NavigationMenuLink>
        <NavigationMenuLink href="#" :class="navigationMenuTriggerStyle()" @click="logout">
          Logout
        </NavigationMenuLink>
      </NavigationMenuItem>
    </NavigationMenuList>
  </NavigationMenu>
</template>
