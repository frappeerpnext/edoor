<template>
    <div id="reservation_chart"></div>
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
        labels: ["Arrival", "Stay Over", "Departure"],
        datasets: [
            {
                name: "Reservation",
                values: [props.param.arrival, props.param.stay_over, props.param.departure],
                type: "pie"
            }
        ]
    };


    const chartConfig = {
        data: data,
        type: "pie",
        height: 250,
        colors: [getStatusColor("Reserved"), getStatusColor("In-house"), getStatusColor("Checked Out")]

    }
    const chart = new Chart("#reservation_chart", chartConfig)

}
onMounted(() => {
    renderChart()
})

</script>