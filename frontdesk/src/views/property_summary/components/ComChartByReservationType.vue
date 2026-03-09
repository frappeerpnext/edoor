<template>
       <ComChart v-if="chartData" height="300px" :chartData="chartData" />
</template>
<script setup>
import { onMounted,ref } from "@/plugin"
import ComChart from "@/components/chart/ComChart.vue"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({param: Object})
const chartData = ref()
function getStatusColor(status) {
    return window.setting.reservation_status.find(r => r.name == status).color
}
function renderChart() {
    chartData.value = {
        legend: {  show:false},
        datasets: [{
            label: {
        show: true,
        position: 'outside', 
        formatter: '{b}: {c} ({d}%)' 
      },
      tooltip: {
            trigger: 'item',  
            formatter: '{b}: {c} ({d}%)' 
            },
            name: 'Reservation Type',
                    height:300,
                    type: 'pie',
                    radius: '55%',
                      data:[
                {
                    value:props.param.total_fit_stay,
                    name:$t('FIT')
                },
                {
                    value:props.param.total_git_stay,
                    name:$t('GIT')
                }
            ],
             type: "pie"
        }],
      
    };


}
onMounted(() => {
    renderChart()
})

</script>