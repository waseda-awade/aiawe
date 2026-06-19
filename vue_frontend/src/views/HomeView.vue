<template>
  <!-- Hero -->
  <div class="bg-muted/40 border-b border-border">
    <div class="container mx-auto max-w-4xl px-4 py-16 md:py-24 text-center">
      <p class="text-sm text-muted-foreground">Waseda University · automated writing evaluation</p>
      <h1 class="text-4xl md:text-5xl font-semibold tracking-tight mt-3">
        Reliable essay scoring, built on open research
      </h1>
      <p class="max-w-xl mx-auto text-muted-foreground mt-4">
        AiAWE evaluates argumentative essays against the ETS TOEFL rubric, giving a
        transparent score with paragraph-level feedback — processed locally, never sent to a
        third party.
      </p>
      <div class="mt-8 flex gap-3 justify-center">
        <router-link :to="{ name: 'dashboard' }">
          <Button class="bg-brand text-brand-foreground hover:bg-brand/90">
            Try it now <ArrowRight class="ml-2 h-4 w-4" />
          </Button>
        </router-link>
        <router-link :to="{ name: 'about' }">
          <Button variant="outline">How it works</Button>
        </router-link>
      </div>
      <p class="mt-4 text-sm text-muted-foreground">
        No account needed to try · create a free account to access additional models.
      </p>
    </div>
  </div>

  <!-- Feature cards -->
  <div class="container mx-auto max-w-4xl px-4 py-12">
    <div class="grid gap-4 sm:grid-cols-3">
      <Card>
        <CardContent class="pt-6">
          <Zap class="h-6 w-6 mb-3 text-brand" />
          <p class="font-medium">Instant scoring</p>
          <p class="text-sm text-muted-foreground mt-1">A score and reasoning in seconds, not days.</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent class="pt-6">
          <Lock class="h-6 w-6 mb-3 text-brand" />
          <p class="font-medium">Private by design</p>
          <p class="text-sm text-muted-foreground mt-1">Submissions processed on Waseda's own servers.</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent class="pt-6">
          <GraduationCap class="h-6 w-6 mb-3 text-brand" />
          <p class="font-medium">Research-backed</p>
          <p class="text-sm text-muted-foreground mt-1">Gemma 3, finetuned on the ETS TOEFL dataset.</p>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ArrowRight, Zap, Lock, GraduationCap } from 'lucide-vue-next'
</script>
