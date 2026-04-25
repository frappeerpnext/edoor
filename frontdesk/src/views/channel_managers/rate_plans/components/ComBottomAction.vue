<template>
  <transition name="dock-slide">
    <div   class="dock">

      <!-- Update Rate -->
      <button
        v-if="!hideUpdateRate"
        class="dock-item update"
        :class="{ 'pulse': selectionCount > 0 && !loading }"
        :disabled="selectionCount === 0 || loading"
        @click="emit('update-rate')"
      >
        <i class="pi pi-dollar icon"></i>

        <span class="label">
          Update Rate
        </span>

        <span
          v-if="selectionCount > 0"
          class="badge"
        >
          {{ selectionCount }}
        </span>
      </button>
      <!-- Update Close Sale -->
<div>    
      <Button
  class="dock-item text-red-400"
  :disabled="selectionCount === 0 || loading"
  :class="{ 'pulse': selectionCount > 0 && !loading }"
  @click="onupdaterestriction"
>
        <i class="pi pi-times icon" v-if="updateRestrictionText=='Open/Close Sale'"></i>
        <i class="pi pi-bars icon" v-else></i>
        <span class="label">
          {{ updateRestrictionText }}
        </span>
        <span
          v-if="selectionCount > 0"
          class="badge"
        >
          {{ selectionCount }}
        </span>
      </Button>

<Menu
  ref="menu"
  :model="RestrictionTypes"
  popup
>
  <template #item="{ item, props }">
    <a v-ripple class="flex items-center gap-2" v-bind="props.action">
      <i :class="item.icon"></i>
      <span>{{ item.label }}</span>
    </a>
  </template>
</Menu>

</div>


      <!-- Clear Selection -->
      <button
        class="dock-item clear"
        :disabled="selectionCount === 0"
        @click="emit('clear-selection')"
      >
        <i class="pi pi-times icon"></i>

        <span class="label">
          Clear Selection
        </span>
      </button>

    </div>
  </transition>
</template>

<script setup>
import { ref,computed  } from 'vue';
const menu = ref();







const props = defineProps({
  hideUpdateRate:Boolean,
  selectionCount: Number,
  loading: Boolean,
  updateRestrictionText:{
    type:String,
    default:"Open/Close Sale"
  },
  selectedRestrictionTypes:Array
})

function toggleMenu(event) {
  if (props.selectedRestrictionTypes.length > 1) {
    menu.value.toggle(event)
  }else{
    emit('update-restriction', props.selectedRestrictionTypes[0])
  }
}
const RestrictionTypes = computed(() => {
  if (props.selectedRestrictionTypes) {
    return props.selectedRestrictionTypes.map(type => ({
      label: type,
      command: () => emit('update-restriction', type)
    }))
  } else {
    return []
  }
})

function onupdaterestriction(event) {
  if (props.selectedRestrictionTypes) {
    toggleMenu(event)
  } else {
    emit('update-restriction')
  }
}
const emit = defineEmits([
  "update-rate",
  "clear-selection",
  "update-restriction"
])
</script>

<style scoped>

/* ===== Dock Container (White-friendly Glass) ===== */

.dock {
  position: fixed;
  bottom: 44px;
  left: 50%;
  transform: translateX(-50%);

  display: flex;
  gap: 12px;

  padding: 10px 12px;

  border-radius: 18px;

  /* Light Glass */
  background: rgba(248, 249, 250, 0.75);

  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);

  border: 1px solid rgba(0,0,0,0.08);

  box-shadow:
    0 8px 22px rgba(0,0,0,0.12);

  z-index: 20;
}

/* ===== Buttons ===== */

.dock-item {
  position: relative;

  display: flex;
  align-items: center;
  gap: 8px;

  padding: 9px 16px;

  border-radius: 12px;

  border: none;

  font-size: 14px;
  font-weight: 500;

  cursor: pointer;

  color: #2c3e50;

  background: rgba(255, 255, 255, 0.85);

  transition: all 0.18s ease;
}

/* Hover */

.dock-item:hover:not(:disabled) {
  transform: translateY(-2px);

  background: white;

  box-shadow:
    0 4px 12px rgba(0,0,0,0.12);
}

/* Active */

.dock-item:active:not(:disabled) {
  transform: scale(0.97);
}

/* Disabled */

.dock-item:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Icons */

.icon {
  font-size: 15px;
}

/* Label */

.label {
  white-space: nowrap;
}

/* Update Accent */

.update:hover:not(:disabled) {
  background: #e6f0ff;
  color: #2563eb;
}

/* Clear Accent */

.clear:hover:not(:disabled) {
  background: #ffecec;
  color: #dc2626;
}

/* Badge */

.badge {
  background: #2563eb;

  color: white;

  font-size: 11px;
  font-weight: 600;

  padding: 2px 7px;

  border-radius: 10px;

  margin-left: 6px;

  min-width: 20px;
  text-align: center;
}

/* ===== Animation ===== */

.dock-slide-enter-active,
.dock-slide-leave-active {
  transition: all 0.22s ease;
}

.dock-slide-enter-from,
.dock-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 16px);
}

/* ===== Update Button Pulse ===== */

.pulse {
  animation: pulseGlow 1.6s ease-in-out infinite;
}

@keyframes pulseGlow {

  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(37, 99, 235, 0);
  }

  50% {
    transform: scale(1.05);
    box-shadow: 0 0 12px rgba(37, 99, 235, 0.35);
  }

  100% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(37, 99, 235, 0);
  }

}
</style>