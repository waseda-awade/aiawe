<template>
  <div class="container mx-auto text-center md:mt-20">
    <h1 class="text-4xl font-bold mb-4">Welcome to AiAWE</h1>
    <div class="text-lg mb-6">
      <p>AiAWE is a project led by John M. Gayed and Judy Wang at Waseda University that evaluates student writing using Large Language Models (LLMs).</p>
      <p>Please go to the <router-link class="text-primary hover:underline" :to="{name: 'about'}">About</router-link> page to learn more about our research.<br /> Click the "Get Started" button below to register and use the app. Below is a screenshot of the app's output. Enjoy!</p>
    </div>
    <router-link :to="{name: 'login'}"><Button>Get Started</Button></router-link>

    <!-- Dashboard Image Section -->
    <div class="mt-8 max-w-3xl mx-auto">
      <img
        src="@/assets/imgs/aiawe-dashboard.png"
        alt="Dashboard Preview"
        class="w-full hover:opacity-90 transition-opacity"
      />
    </div>

    <!-- Modal for image preview -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="showModal = false">
      <div class="relative max-h-[90vh] max-w-[90vw]">
        <img
          src="@/assets/imgs/aiawe-dashboard.png"
          alt="Dashboard Preview"
          class="max-h-[90vh] max-w-[90vw] object-contain"
        />
        <button
          class="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full w-8 h-8 flex items-center justify-center"
          @click="showModal = false"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Button from '@/components/ui/button/Button.vue';

const showModal = ref(false);
</script>

<style scoped>
.max-w-400 {
  max-width: 400px;
}
</style>
