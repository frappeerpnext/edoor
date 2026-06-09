<template> 
    <div class="card">
        <DataTable :value="channelManagerData?.payment_types" stripedRows tableStyle="min-width: 50rem">
            <Column field="payment_type_code" :header="$t('Payment Type Code')"></Column>
            <Column field="payment_type_name" :header="$t('Payment Type Name')"></Column>
            <Column field="payment_type_title" :header="$t('Payment Type Title')"></Column> 
            <Column :header="$t('eDoor Payment Type Code')">
                <template #body="slotProps">
                    {{bookingGuaranteeMap[slotProps.data.edoor_payment_type_code] || '-'}}
                </template>
            </Column>  
        </DataTable>
    </div> 

 
</template>
<script setup>
import {ref, computed, onMounted} from 'vue'
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'

const { channelManagerData } = useCMDashboard()

const bookingGuarantee = ref([])


// Convert array to lookup object
const bookingGuaranteeMap = computed(() => {
    return bookingGuarantee.value.reduce((acc, item) => {
        acc[item.name] = item.booking_guarantee_name
        return acc
    }, {})
})

async function getBookingGuarantee() {
    const res = await app.getDocList('Booking Guarantee', {
        fields: ['name', 'booking_guarantee_name'],
        orderBy: {
            field: 'creation',
            order: 'desc'
        }
    })

    if (res?.data) {
        bookingGuarantee.value = res.data
    }
}

onMounted(async () => {
    await getBookingGuarantee()
})
</script>