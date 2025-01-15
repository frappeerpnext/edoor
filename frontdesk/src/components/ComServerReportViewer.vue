<template>
    <div>
     
        <div id="viewer"></div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "@/plugin"
const props = defineProps({
    report_name: String,
    params:[]
})

onMounted(() => {
    let report_params = props.params
     
    const build_in_params = [
        {name: 'printed_by', values: [window.user.full_name] },
        {name: 'property', values: [window.property_name] }
    ]
    report_params = [...report_params, ...build_in_params]

    $("#viewer").boldReportViewer({
        reportServerUrl:window.setting.server_report_url,
        reportServiceUrl: window.setting.report_service_url,
        reportPath: props.report_name,
        serviceAuthorizationToken: "bearer " + window.setting.embed_code,
        parameters: report_params,
        zoomFactor: 1.25,
        toolbarSettings: {
                        items: ej.ReportViewer.ToolbarItems.All
        }
    });
});
</script>

<style scoped>
#viewer {
    min-height: 75vh;
    width: 100%;
}
 
</style>