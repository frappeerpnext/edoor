<template> 
    <div class="card">
        <DataTable :value="channelManagerData?.services" stripedRows tableStyle="min-width: 50rem">
            <Column field="services_code" :header="$t('Services Code')"></Column>
            <Column field="service_name" :header="$t('Service Name')"></Column>
            <Column :header="$t('eDoor Service Code')">
                <template #body="slotProps">
                    {{accountCodeMap[slotProps.data.edoor_service_code] || '-'}}
                </template>
            </Column>  
        </DataTable>
    </div> 

 
</template>
<script setup>
import {ref, onMounted, computed } from 'vue'
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'

const { channelManagerData } = useCMDashboard()


const accountCode = ref([])

// Convert array to lookup object
const accountCodeMap = computed(() => {
    return accountCode.value.reduce((acc, item) => {
        acc[item.name] = item.account_name
        return acc
    }, {})
})

const getAccCode = computed(() => {
    return channelManagerData.value
})

async function getAccountCode(accCode) {
    const res = await app.getDocList('Account Code', {
        filters: [ 
            ['name', 'in', accCode]
        ],
        fields: ['name', 'account_name'],
        orderBy: {
            field: 'creation',
            order: 'desc'
        },
        limit: 50
    })

    if (res?.data) {
        accountCode.value = res.data 
    }
}

onMounted(async () => {
    const accCode = [...new Set(getAccCode.value?.services?.map(x => x.edoor_service_code))]
    await getAccountCode(accCode) 
})
</script>