<template>
    <div class="card">
        <DataTable :value="channelManagerData?.room_types" stripedRows tableStyle="min-width: 50rem">
            <Column field="room_type_code" :header="$t('Room Type Code')" />

            <Column field="room_type_name" :header="$t('Room Type Name')" />

            <Column :header="$t('eDoor Room Type')">
                <template #body="slotProps">
                    {{
                        roomTypeMap[slotProps.data.edoor_room_type] || '-'
                    }}
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'

const { channelManagerData } = useCMDashboard()

const roomType = ref([])

/**
 * Convert array to lookup object
 * {
 *   "DLX": "Deluxe Room",
 *   "STD": "Standard Room"
 * }
 */
const roomTypeMap = computed(() => {
    return roomType.value.reduce((acc, item) => {
        acc[item.name] = item.room_type
        return acc
    }, {})
})

async function getRoomTypeName() {
    const res = await app.getDocList('Room Type', {
        filters: {
            property: window.property.name,
            disabled: ['!=', 1]
        },
        fields: ['name', 'room_type'],
        orderBy: {
            field: 'creation',
            order: 'desc'
        }
    })

    if (res?.data) {
        roomType.value = res.data
    }
}

onMounted(async () => {
    await getRoomTypeName()
})
</script>