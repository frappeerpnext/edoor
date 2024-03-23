<template>
    <div id="reservation_type_chart"></div>
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
        labels: [$t("FIT"), $t("GIT")],
        datasets: [
            {
                name: "Reservation Type",
                values: [props.param.total_fit_stay,props.param.total_git_stay],
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