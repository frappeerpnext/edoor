<template>
    <div class="relative">
        <div v-if="showPercentage" class="absolute top-50 left-50 text-6xl" :class="class" style="transform: translate(-50%, -50%);">
            <span :style="{ color: percentage.color }" v-if="showPercentageInteger">{{ parseInt(percentage.percent) }}%</span>
            <span :style="{ color: percentage.color }" v-else>{{ percentage.percent }}%</span>
        </div>
        <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full" width="225" height="150" />
    </div>
</template>
<script setup>
import { ref, computed, inject } from 'vue'
const gv = inject('$gv')
const props = defineProps({
    total_room:Number,
    data: {
        type: Array,
        default: []
    },
    showPercentage: {
        type: String,
        default: ''
    },
    cutout: {
        type: String,
        default: '70%'
    },
    isLegend: {
        type: Boolean,
        default: true
    },
    class: String,
    showPercentageInteger:Boolean
})
const chartOptions = ref({
    cutout: props.cutout,
    plugins: {
        legend: {
            display: props.isLegend,
        },
    }
});
const percentage = ref({
    percent: '',
    field_show: 0,
    total: 0,
    color: '#000'
})
// [{label: '', value: 0, color: ''}]
const chartData = computed(() => {

    // const documentStyle = getComputedStyle(document.body);
    let labels = []
    let values = []
    let backgroundColors = []
    percentage.value.total = 0
    if (props.data.length > 0) {
        props.data.forEach((r) => {
            labels.push(r.label)
            values.push(r.value)
            backgroundColors.push(r.color || 'rgba(255, 159, 64)')
            if (props.showPercentage) {
                percentage.value.total = percentage.value.total + r.value
                if (r.label == props.showPercentage) {
                    percentage.value.field_show = r.value
                    percentage.value.color = r.color
                }
            }
        })
        // calculate
        const total_room = (props.total_room ?? 0) == 0? 1: props.total_room
        const percent = (percentage.value.field_show / total_room) * 100

        percentage.value.percent = gv.numberFormat(percent)
        return {
            labels: labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: backgroundColors
                }
            ]
        }
    } else {
        return []
    }

})

const chartDatax = ref();

const documentStyle = getComputedStyle(document.body);
chartDatax.value = {
    datasets: [
        {
            data: [21, 12],
            backgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-color'), documentStyle.getPropertyValue('--bg-warning-color'), documentStyle.getPropertyValue('--green-500')],
            hoverBackgroundColor: [documentStyle.getPropertyValue('--bg-btn-green-hover'), documentStyle.getPropertyValue('--bg-warning-hover'), documentStyle.getPropertyValue('--green-400')]
        }
    ],
}
</script>
