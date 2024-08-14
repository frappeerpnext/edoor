<template>
    <ComOwnerContentTitle :label="'Room Type Sales - '+ moment(date).format('DD-MM-YYYY')">
        <div class="col w-full p-0">
            <Skeleton v-if="loading" class="mb-2" v-for="index in 3" :key="index" width="100%" height="50px"></Skeleton>
            <template v-else>
                <div class="flex">
                    <div class="col-12 p-0">
                        <ComOwnerBarChartLine :data="data" />
                    </div>
                </div>
            </template>
        </div>

    </ComOwnerContentTitle>
</template>
<script setup>
import { ref, onMounted, getApi, computed,defineProps,watch,inject } from '@/plugin'
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import ComOwnerBarChartLine from '@/views/dashboard/components/ComOwnerBarChartLine.vue'
import TabView from 'primevue/tabview';
const loading = ref(true)
const moment = inject('$moment')
const data = ref({})
const props = defineProps({
    date: {
        type: Date,
    },
});

function renderdata() {
    loading.value = true
    const doc = getApi('frontdesk.get_room_type_chart_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: props.date
    })
        .then((result) => {
            loading.value = false
            data.value = result.message
        })
        .catch((error) => {
            loading.value = true
        });
}
watch(() => props.date, (newDate) => {
    if (newDate) {
        renderdata();
    }
});

onMounted(() => {
    renderdata()

})         
</script>
<style scope>
.p-tabview-panels {
    padding: 10px 0px 0px 0px;
}
</style>