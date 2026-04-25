<template>
    <Message class="upload-notice" :closable="false">
    <div class="flex gap-3 align-items-center">
      <div>
        <ComIcon :icon="icon" :height="height + 'px'" />
      </div>
      <div>
        <div class="font-semibold text-2xl">{{ $t(label) }}</div>
        <p>{{ $t(text) }}</p>
      </div>
    </div>
  </Message>
</template>
<script setup> 
const props = defineProps({
    label: {
        type: String,
        default: ''
    },
    text: {
        type: String,
        default: 'confirmation message description goes here. Please review the details before proceeding.'
    },
    icon: {
        type: String,
        default: 'iconPurpleLightBulb'
    },
    height: {
        type: Number,
        default: 40
    }
})
</script>
<style scoped>
</style>