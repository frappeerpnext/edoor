<template>
    <div id="reservation_chart"></div>
</template>
<script setup>
import { onMounted } from "@/plugin"
import { Chart } from "frappe-charts/dist/frappe-charts.min.esm"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({param: Object})

function getStatusColor(status) {
    return window.setting.reservation_status.find(r => r.name == status).color
}
function renderChart() {
    const data = {
        labels: [$t("Arrival"), $t("Stay Over"), $t("Departure"),$t("N/S Reserved Room")],
        datasets: [
            {
                name: "Reservation",
                values: [props.param.arrival, props.param.stay_over, props.param.departure, props.param.total_no_show],
                type: "pie"
            }
        ],
        
    };


    const chartConfig = {
        data: data,
        type: "pie",
        height: 250,
        colors: [getStatusColor("Reserved"), getStatusColor("In-house"), getStatusColor("Checked Out"),getStatusColor("No Show")],
        valuesOverPoints: 1
    }
    const chart = new Chart("#reservation_chart", chartConfig)

}
onMounted(() => {
    renderChart()
})

</script>