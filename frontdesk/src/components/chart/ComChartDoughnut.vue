<template>

    <div class="relative">
        <div v-if="showPercentage" class="absolute top-50 left-50 text-6xl" :class="class" style="transform: translate(-50%, -50%);">
            <span :style="{ color: percentage.color }">{{ occupancy }}%</span>
        </div>
         
        <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full" width="225" height="150" />
    </div>
</template>
<script setup>
import { ref, inject,computed } from 'vue'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
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
    percentage: {
        type: Number,
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

const occupancy = computed(()=>{
    
    if (props.showPercentageInteger){
        return props.percentage?.toFixed(0)
    }else {
        return props.percentage?.toFixed(2)
    }
  

})

const chartData = computed(()=>{ 
    let labels = ref([])
    let values = ref([])
    let backgroundColors = []
    if (props.data.length > 0) {
        props.data.forEach((r) => {
            labels.value.push($t(r.label))
            values.value.push(r.value)
            backgroundColors.push(r.color || 'rgba(255, 159, 64)')
            if (props.showPercentage) {
                percentage.value.total = percentage.value.total + r.value
                if (r.label == props.showPercentage) {
                    percentage.value.field_show = r.value
                    percentage.value.color = r.color
                }
            }
        })
           
        return {
            labels:  labels.value,
            datasets: [
                {
                    data: values.value,
                    backgroundColor: backgroundColors
                }
            ]
        }
    } else {
        return []
    }

})

 

</script>
