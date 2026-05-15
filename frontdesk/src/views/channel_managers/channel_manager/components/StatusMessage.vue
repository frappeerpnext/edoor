<template>
  <transition name="smooth-alert">
    <div 
      v-if="show"
      :class="[
        'p-4 border-round border-left-3 shadow-sm mb-4',
        severityClasses
      ]"
    >
      <div class="flex align-items-start">
        <i :class="['pi mr-3 text-xl mt-1', iconClass]"></i>

        <div class="flex-grow-1">
          <span class="block font-bold text-lg line-height-1 mb-2">
            {{ title }}
          </span>

          <p class="m-0 text-sm opacity-80 line-height-3">
            <slot>{{ message }}</slot>
          </p>
        </div>

        <Button 
          v-if="closable" 
          icon="pi pi-times" 
          class="p-button-rounded p-button-text p-button-sm -mt-2 -mr-2" 
          @click="$emit('close')" 
        />
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  show: Boolean,
  status: String, // 'Complete', 'Pending', 'Error'
  title: String,
  message: String,
  closable: Boolean
});

defineEmits(['close']);

const severityClasses = computed(() => {
  switch (props.status) {
    case 'Complete': return 'bg-green-50 border-green-500 text-green-900';
    case 'Pending':  return 'bg-orange-50 border-orange-500 text-orange-900';
    case 'Error':    return 'bg-red-50 border-red-500 text-red-900';
    default:         return 'bg-blue-50 border-blue-500 text-blue-900';
  }
});

const iconClass = computed(() => {
  switch (props.status) {
    case 'Complete': return 'pi-check-circle text-green-600';
    case 'Pending':  return 'pi-exclamation-triangle text-orange-600';
    case 'Error':    return 'pi-times-circle text-red-600';
    default:         return 'pi-info-circle text-blue-600';
  }
});
</script>

<style scoped>
.smooth-alert-enter-active,
.smooth-alert-leave-active {
  transition:
    opacity 0.5s ease,
    transform 0.5s ease,
    max-height 0.5s ease,
    margin 0.5s ease,
    padding 0.5s ease;
  overflow: hidden;
}

.smooth-alert-enter-from,
.smooth-alert-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
  margin-bottom: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

.smooth-alert-enter-to,
.smooth-alert-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 300px;
}
</style>