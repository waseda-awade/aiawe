<template>
  <div class="container mx-auto text-center mt-20">
    <h1 class="text-4xl font-bold mb-4">Welcome to AiAWE</h1>
    <div class="text-lg mb-6 max-w-400 mx-auto">
      <p>AiAWE is a project led by John M. Gayed and Judy Wang at Waseda University that evaluates student writing using Large Language Models (LLMs).</p>
      <p>Please go to the <router-link class="text-gray-500 hover:cursor-pointer" :to="{name: 'home'}">About</router-link> page to learn more about our research.</p>
    </div>
    <router-link :to="{name: 'login'}"><Button>Get Started</Button></router-link>
  </div>
</template>

<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
</script>
