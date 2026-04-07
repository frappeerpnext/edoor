<template>
    <div class="flex flex-column gap-2">
       
        <div class="flex align-items-center justify-content-between mb-2">

    <!-- Left -->
    <div class="flex align-items-center gap-2">

        <i class="pi pi-home text-primary text-xl"></i>

        <span class="text-xl font-semibold">
            Room Types
        </span>

    </div>

    <!-- Right (Selected Count) -->
    <span
        v-if="selectedRooms.length"
        class="text-sm text-color-secondary"
    >
        {{ roomTypes.filter(x=>x.selected).length }} selected
    </span>

</div>
        <div
            v-for="room in roomTypes"
            :key="room.cm_room_type"
            class="room-row flex align-items-center justify-content-between p-3 border-round cursor-pointer transition-all transition-duration-200"
            :class="{
                'selected-row': room.selected
            }"
            @click="toggleRoom(room)"
        >

            <!-- Left Side -->
            <div class="flex flex-column">

                <!-- Room Name -->
                <div class="text-lg font-semibold">
                    {{ room.room_type_name }} ({{ room.room_type_alias  }})
                 
                </div>

                <!-- Alias -->
                <div class="text-sm text-color-secondary">
                    Code: {{ room.cm_room_type }}
                </div>

            </div>

            <!-- Right Side -->
            <div class="flex align-items-center gap-2">

          

                <!-- Check Icon -->
                <i
                    v-if="room.selected"
                    class="pi pi-check-circle text-green-500 text-xl"
                />

            </div>

        </div>

    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'

const props = defineProps({

    multiple: {
        type: Boolean,
        default: false
    },

    modelValue: {
        type: Array,
        default: () => []
    }
})
const {
    roomTypes,
    reloadRoomRatesData
} = useRatePlan()

const emit = defineEmits(['update:modelValue'])

const selectedRooms = ref([...props.modelValue])

const isSelected = (id) => {
    return selectedRooms.value.includes(id)
}

const toggleRoom = async(rt) => {
    
    const _selected = roomTypes.value.find(r=>r.selected)
    if(_selected){
        if(_selected.edoor_room_type == rt.edoor_room_type) return
         _selected.selected = false
    }

    rt.selected = true
    await reloadRoomRatesData();

}

// sync from parent
watch(() => props.modelValue, (val) => {
    selectedRooms.value = [...val]
})
</script>

<style scoped>

.room-row {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

.room-row:hover {
    border-color: var(--primary-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.selected-row {
    border-color: var(--primary-color);
    background: var(--primary-50);
}

.alias-badge {
    background: var(--surface-200);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

</style>