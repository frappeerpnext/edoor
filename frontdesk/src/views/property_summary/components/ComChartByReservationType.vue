<template>
    <div id="reservation_type_chart"></div>
</template>
<script setup>
import { onMounted } from "@/plugin"
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"

const props = defineProps({param: Object})

function getStatusColor(status) {
    return window.setting.reservation_status.find(r => r.name == status).color
}
function renderChart() {
    const data = {
        labels: ["FIT", "GIT"],
        datasets: [
            {
                name: "Reservation Type",
                values: [props.param.fit_reservation_arrival + props.param.fit_stay_arrival,props.param.git_reservation_arrival + props.param.git_stay_arrival],
                type: "pie"
            }
        ],
      
    };


    const chartConfig = {
        data: data,
        type: "pie",
        height: 250,
        valuesOverPoints: 1

    }
    const chart = new Chart("#reservation_type_chart", chartConfig)

}
onMounted(() => {
    renderChart()
})

</script>