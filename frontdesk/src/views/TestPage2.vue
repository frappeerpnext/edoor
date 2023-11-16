<template>
  <div class="card flex justify-content-center">
      <Calendar v-model="date" class="p-invalid" />
  </div>
</template>

<script setup>
import { ref } from "vue";

const date = ref();
</script>
