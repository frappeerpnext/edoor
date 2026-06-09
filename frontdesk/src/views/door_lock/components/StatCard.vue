<template>
  <div
    class="surface-card p-3 border-round shadow-1 border-left-3"
    :class="borderClass"
  >
    <div class="flex justify-content-between align-items-center mb-2">
      <span
        class="text-xs font-bold uppercase"
        :class="titleClass || 'text-500'"
      >
        {{ title }}
      </span>

      <i
        :class="[icon, iconClass, 'text-lg']"
      />
    </div>

    <div
      class="text-2xl font-bold"
      :class="valueClass || 'text-900'"
    >
      {{ value }}
    </div>

    <span
      class="text-xs"
      :class="subtitleClass || 'text-400'"
    >
      {{ subtitle }}
    </span>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  subtitle: String,
  icon: String,
  borderClass: String,
  iconClass: String,
  titleClass: String,
  valueClass: String,
  subtitleClass: String
})
</script>