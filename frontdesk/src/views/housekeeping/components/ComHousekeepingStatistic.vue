<template>
    <div>
        <ComPanel title="Today Statistic" class=" pb-3">

            <ComChartDoughnut :percentage="data?.occupancy" :data="chartData"
                v-if="chartData.length > 0" show-percentage="Occupied" class="doughnut__chart_ds" />
            <ComHousekeepingTodaySummary :isHousekeeping="true" />
        </ComPanel>
        <ComPanel title="Housekeeping Statistic" class="mt-3 pb-3">
            <ComHousekeepingStatus />
        </ComPanel>
    </div>
</template>
<script setup>
import { ref, getApi, watch, inject, onMounted, onUnmounted } from "@/plugin"
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComHousekeepingTodaySummary from './ComHousekeepingTodaySummary.vue';
const data = ref({})
const chartData = ref([])
const props = defineProps({ date: "", offSocket: true })
const gv = inject("$gv")
const loading = ref(false)

const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))


watch(() => [props.date], ([newValue]) => {
    loadData(newValue)
})
onMounted(() => {
    window.socket.on("ComHousekeepingStatistic", (arg) => {

        if (arg.property == window.property_name) {
            loadData(props.date)
        }
    })

    loadData(props.date)
})
function loadData(date) {
    loading.value = true
    chartData.value = []
    const currentDate = ref(working_day?.date_working_day)
    if (date) {
        currentDate.value = gv.dateApiFormat(date)
    }
    getApi('frontdesk.get_dashboard_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: currentDate.value
    }).then((result) => {
        loading.value = false
        data.value = result.message
        const documentStyle = getComputedStyle(document.body);
        chartData.value.push({ label: 'Occupied', value: data.value.total_room_occupy, color: documentStyle.getPropertyValue('--bg-btn-green-color') })
        chartData.value.push({ label: 'Vacant', value: data.value.total_room_vacant, color: documentStyle.getPropertyValue('--bg-warning-color') })
    }).catch((err) => {
        loading.value = false
    })
}

onUnmounted(() => {
    window.socket.off("ComHousekeepingStatistic")
})

</script>