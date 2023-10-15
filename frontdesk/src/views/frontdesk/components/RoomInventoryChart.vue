
<template>
    <div class="card" style="background:#fff; margin-bottom: 20px; border-radius: 10px; padding:10px; ">
 
 
        <Chart type="bar" :data="chartData" :options="chartOptions" class="h-30rem"   :plugins="plugins"/>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, inject } from "vue";
import ChartDataLabels from 'chartjs-plugin-datalabels';
const plugins = [ChartDataLabels]
const props = defineProps({ data: Object })
const moment = inject("$moment")

onMounted(() => {
    chartOptions.value = setChartOptions();
});

const chartData = computed(() => {
    const documentStyle = getComputedStyle(document.documentElement);

    return {
        labels: [...new Set(props.data.map(r=>moment(r.start).format("DD/MMM")))].slice(0,-1),
        datasets: [
            {
                type: 'line',
                label: 'Occupancy',
                borderColor: documentStyle.getPropertyValue('--blue-500'),
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                data: props.data.filter(r=>r.occupancy) .map(r=>parseFloat( r.occupancy)),
                showPoint:true
            },
          
            
           
            {
                type: 'bar',
                label: 'Departure',
                backgroundColor: window.setting.reservation_status.find(r=>r.reservation_status=="Checked Out").color,
                data:  props.data.filter(r=>r.departure) .map(r=>parseFloat( r.departure))
            },
                {
                    type: 'bar',
                    stacked: false,
                    label: 'Stay Over',
                    backgroundColor: window.setting.reservation_status.find(r=>r.reservation_status=="In-house").color,
                    data:   props.data.filter(r=>r.stay_over) .map(r=>parseFloat( r.stay_over))
                },
            {
                type: 'bar',
                label: 'Arrival',
                stacked: false,
                backgroundColor: window.setting.reservation_status.find(r=>r.reservation_status=="Reserved").color,
                data:   props.data.filter(r=>r.arrival) .map(r=>parseFloat( r.arrival)),
                borderColor: 'white',
            },
           
        ]
    };
})
const chartOptions = ref();


const setChartOptions = () => {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    return {
        maintainAspectRatio: false,
        aspectRatio: 0.6,
         plugins: {
           
            tooltips: {
                mode: 'index',
                intersect: true
            },
            legend: {
                labels: {
                    color: textColor
                }
            },
        
        },
        scales: {
            x: {
                stacked:true,
                ticks: {
                    color: textColorSecondary
                },
               
            },
            y: {
                stacked:true,
                ticks: {
                    color: textColorSecondary
                },
                
            }
        }
    };
}
</script>
