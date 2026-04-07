<template>
  <ComOverlayPanelContent 
    hideButtonOK 
    style="min-width:20rem;max-width:35rem;" 
    title="Change Child" 
    @onCancel="$emit('onClose')"
  >
    <div class="mb-4">
      <table class="w-full mt-2" v-if="list_occupancy_code.length">
        <tr v-for="o in list_occupancy_code" :key="o.name">
          <td class="p-2">
            <label class="p-label mb-2">{{ o.title }}</label>
          </td>
          <td class="p-2 w-8rem">
            <InputNumber 
              v-model="o.value"      
              inputClass="w-full"  
              showButtons
              :min="0" 
              :max="10" 
              class="child-adults-txt"
            />
          </td>
        </tr>
      </table>

      <!-- show message if no child allowed -->
      <div v-else class="text-gray-500 p-3 text-center">
        {{ $t('No child allowed for this room') }}
      </div>
    </div>

    <template #footer-right>
      <Button 
        :label="$t('OK')" 
        @click="onSubmit"
        :disabled="!list_occupancy_code.length"
      />
    </template>
  </ComOverlayPanelContent>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import { getDocList,getApi } from "@/plugin"
import { i18n } from '@/i18n'

const { t: $t } = i18n.global
const emit = defineEmits(['update:modelValue', 'onClose', 'submit'])

const props = defineProps({
  room: String,
  modelValue: {
    type: Array,
    default: () => []
  }
})

const list_occupancy_code = ref([])
const room_type = ref(null) // optional if needed for display

// Load occupancy codes on mount
onMounted(async () => {
  await loadOccupancyCodes(props.room)
})

// Watch for room change
watch(() => props.room, async (newRoom) => {
  if (!newRoom) return
  await loadOccupancyCodes(newRoom)
})

// Function to load occupancy codes
async function loadOccupancyCodes(room) {
    if (props.modelValue.length) {
    list_occupancy_code.value = props.modelValue
  }else{
  const occupancyCodes = await getDocList("Occupancy Code", {
    fields: ["name", "title"],
    filters: { is_child: 1 }
  })

  let allowedCodes = []
  allowedCodes = await getApi('reservation.get_room_type_occupancy_codes', { room_type_id: room })
  
  allowedCodes = allowedCodes.message || []
  console.log('Model Value:', props.modelValue)
  const allowedSet = new Set(allowedCodes.map(c => c.occupancy_code))

    list_occupancy_code.value = occupancyCodes
  .filter(o => allowedSet.has(o.name))   // only keep matching codes
  .map(o => ({ 
    ...o, 
    value: 0                            // default value 0
  }))
  }
  
}

// Submit handler
function onSubmit() {
  const childlist = list_occupancy_code.value
  emit('update:modelValue', childlist) // optional v-model
  emit('onChangeChild', childlist)     // custom event for parent
  emit('onClose')
}
</script>