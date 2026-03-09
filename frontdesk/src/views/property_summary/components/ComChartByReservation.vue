<template>
    <ComChart v-if="chartData" height="300px" :chartData="chartData" />
</template>
<script setup>
import { onMounted, ref } from "@/plugin"
import ComChart from "@/components/chart/ComChart.vue"
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({ param: Object })
const chartData = ref()
function getStatusColor(status) {
    return window.setting.reservation_status.find(r => r.name == status).color
}
function renderChart() {
    chartData.value = {
        legend: {  show:false},
     
        datasets:
            [
                {
                    name: 'Traffic Sources',
                    height:300,
                    type: 'pie',
                    radius: '55%',
                    label: {
        show: true,
        position: 'outside', 
        formatter: '{b}: {c} ({d}%)' 
      },
      tooltip: {
    trigger: 'item', 
    formatter: '{b}: {c} ({d}%)'
  },
                    data: [{
                        value: props.param.arrival, name: $t("Arrival"), itemStyle: {
                            color: getStatusColor("Reserved")
                        }
                    },
                    {
                        value: props.param.departure, name: $t("Departure"), itemStyle: {
                            color: getStatusColor("Checked Out")
                        }
                    },
                    {
                        value: props.param.stay_over, name: $t("Stay Over"), itemStyle: {
                            color: getStatusColor("In-house")
                        }
                    },
                    {
                        value: props.param.total_no_show, name: $t("N/S Reserved Room"), itemStyle: {
                            color: getStatusColor("No Show")
                        }
                    },]

                }

            ],


    };

 
}
onMounted(() => {
    renderChart()
})

</script>