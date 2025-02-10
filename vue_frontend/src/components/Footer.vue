<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="py-6 border-t">
    <div class="container mx-auto px-4">
      <div class="text-center text-sm text-muted-foreground">
        <p>&copy; {{ currentYear }} Waseda University. All rights reserved.</p>
        <div class="mt-2 space-x-4">
          <router-link :to="{ name: 'terms' }" class="hover:text-primary transition-colors">
            Terms of Service & Privacy Policy
          </router-link>
          <a href="mailto:admin@aiawe.app" class="hover:text-primary transition-colors">
            Contact Us
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
