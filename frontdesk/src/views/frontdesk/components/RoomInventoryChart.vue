
<template>
    <div class="card" style="background:#fff; margin-bottom: 20px; border-radius: 10px; padding:10px; ">

        <ComChart v-if="chartData"   :chartData="chartData" />

    </div>
</template>

<script setup>
import {  inject,watch,ref } from "vue";

import ComChart from "@/components/chart/ComChart.vue"
const props = defineProps({ data: Object })
const moment = inject("$moment")
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const chartData = ref()

watch(() => props.data, (newValue, oldValue) => {
    renderChart();
})


function renderChart(){
 
     chartData.value = {
        labels: [...new Set(props.data.map(r=>moment(r.start).format("DD/MMM")))],
        datasets: [
            {
                stack:"stack_key",
                type: 'bar',
                name: $t('Departure'),
                data:  props.data.filter(r=>r.departure>=0).map(r=>parseFloat( r.departure)),
                itemStyle: {
                    color: getStatusColor("Checked Out")
                }

            },
                {
                    stack:"stack_key",
                    type: 'bar',
                    name: $t('Stay Over'),
                   
                    data:   props.data.filter(r=>r.stay_over>=0) .map(r=>parseFloat( r.stay_over)),
                    itemStyle: {
                    color: getStatusColor("In-house")
                }
                
                },
            {
                type: 'bar',
                stack:"stack_key",
                name: $t('Arrival'),
                data:   props.data.filter(r=>r.arrival>=0) .map(r=>parseFloat( r.arrival)),
                itemStyle: {
                    color: getStatusColor("Reserved")
                }
                
            },
            {
                type: 'line',
                name: $t('Occupancy'),
                data: props.data.filter(r=>r.occupancy) .map(r=>parseFloat( r.occupancy)),
                label: {
                    show: true,          // Show label with value
                    position: 'top',      // Position the label above the point
                    color: '#000',        // Set label color (optional)
                    fontSize: 14          // Adjust font size (optional)
             }
            },
           
        ]
    }
 

    }

    function getStatusColor(status){
        return window.setting.reservation_status.find(r=>r.name==status).color
    }


</script>
