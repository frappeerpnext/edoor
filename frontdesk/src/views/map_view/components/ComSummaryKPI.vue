<template>
  <div class="grid bg-white card border-round-lg">
<div v-for="(s, index) in report_summary" :key="index" class="col p-3" :class="s.indicator">
  <div class="white-space-nowrap text-center">
 {{ s.label }}
  </div>   
 
      <div class="text-center mt-2" :style="'color:' + s.indicator"> {{ s.value }}</div>

    </div>
  </div>
      
</template>
<script setup>
import { ref } from "@/plugin"
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
 
const props = defineProps({
  report_summary:Object
})
 

</script>