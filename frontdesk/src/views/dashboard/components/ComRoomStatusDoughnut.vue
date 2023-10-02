<template>
    <div class="main_doughnut">
        <div class="doughnut_percent text-color-chart"> 12<!-- {{ (data.total_room_occupy / (data.total_room_occupy + data.total_room_vacant)) * 100 }}% --></div>
        <div class="card flex justify-content-center">
            <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full w-17rem" />
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted,watch } from "vue";
import Chart from 'primevue/chart';

const props = defineProps({
    data: Object
})

onMounted(() => {
    const documentStyle = getComputedStyle(document.body);
    chartData.value = {
        datasets: [
            {
                data: [props.data.total_room_occupy, props.data.total_room_vacant],
                backgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-color'), documentStyle.getPropertyValue('--bg-warning-color'), documentStyle.getPropertyValue('--green-500')],
                hoverBackgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-hover'), documentStyle.getPropertyValue('--bg-warning-hover'), documentStyle.getPropertyValue('--green-400')]
            }
        ],
    }
});

const chartData = ref();

const chartOptions = ref({
    cutout: '70%',
});

</script>
<style scoped>
.main_doughnut {
    position: relative;
}

.doughnut_percent {
    white-space: nowrap;
    position: absolute;
    left: 50%;
    top: 52%;
    font-size: 40px;
    transform: translate(-50%, -50%);
}
</style>
