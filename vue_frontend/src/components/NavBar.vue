<template>
  <nav class="bg-gray-800 text-white p-4">
    <div class="container mx-auto flex justify-between items-center">
      <a href="#" class="text-xl font-bold">VueApp</a>
      <div>
        <router-link to="/" class="mx-2 hover:underline">Home</router-link>
        <router-link to="/login" class="mx-2 hover:underline">Login</router-link>
      </div>
    </div>
  </nav>
</template>
