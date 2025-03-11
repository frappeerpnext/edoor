<template>
     
        <Splitter class="mb-5" style="height:calc(100vh - 110px) ;" state-key="report_spliter_state" state-storage="local">
            <SplitterPanel :size="25" class="pa-4 left-side-panel overflow-y-auto">
                <ComReportTree   @onSelectReport="onSelectReport" />
            </SplitterPanel>

            <SplitterPanel :size="75" class="pa-4">
           
                <div id="main_server_report_viewer"></div>
            </SplitterPanel>
        </Splitter>
      

</template>
<script setup>
import { ref, onMounted, inject,onUnmounted } from "@/plugin"
import ComReportTree from "@/views/report/components/ComReportTree.vue"
 
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const moment = inject("$moment")
 
const setting = window.setting
 
const gv = inject("$gv")

 
const selectedReport = ref()
 

function onSelectReport(p) { 
    
    selectedReport.value = p
    let report_params = [
        {name: 'printed_by', values: [window.user.full_name] },
        {name: 'username', values: [window.user.name] },
        {name: 'property', values: [window.property_name] },
        {name: 'start_date', values: ['2025-01-01'] },
        {name: 'end_date', values: ['2025-01-31'] },
    ] 
    
    if(selectedReport.value.filter_default_value){
        const default_filter = JSON.parse(selectedReport.value.filter_default_value)
 
        if( default_filter.start_date){
            report_params = report_params.filter(r=>r.name!='start_date')
            report_params.push({name: 'start_date', values: [get_date_by_timestamp(default_filter.start_date)] })
        }
        if( default_filter.end_date){
           
            report_params = report_params.filter(r=>r.name!='end_date')
            report_params.push({name: 'end_date', values: [get_date_by_timestamp(default_filter.end_date)] })
           
        }
       
        if (default_filter.row_group){
            report_params.push({name: 'row_group', values: [default_filter.row_group] })
        }
        if (default_filter.order_by){
            report_params.push({name: 'order_by', values: [default_filter.order_by] })
        }
        if (default_filter.group_by){
            report_params.push({name: 'group_by', values: [default_filter.group_by] })
        }
        if (default_filter.show_package_breakdown){
            report_params.push({name: 'show_package_breakdown', values: [default_filter.show_package_breakdown] })
            
        }
        if (default_filter.show_all_breakdown){
            report_params.push({name: 'show_all_breakdown', values: [default_filter.show_all_breakdown] })
        }
        if (default_filter.show_all_breakdown){
            report_params.push({name: 'show_all_breakdown', values: [default_filter.show_all_breakdown] })
        }
        if (default_filter.status){
            report_params.push({name: 'status', values: [default_filter.status] })
        }
        if (default_filter.group_by_date){
            report_params.push({name: 'group_by_date', values: [default_filter.group_by_date] })
        }
        if (default_filter.group_by_date){
            report_params.push({name: 'group_by_date', values: [default_filter.group_by_date] })
        }
        if (default_filter.show_chart){
            report_params.push({name: 'show_chart', values: [default_filter.show_chart] })
        }
        if (default_filter.show_summary){
            report_params.push({name: 'show_summary', values: [default_filter.show_summary] })
        }
        if (default_filter.show_occupy_only){
            report_params.push({name: 'show_occupy_only', values: [default_filter.show_occupy_only] })
        }
        

        

        

    }
 
    $("#main_server_report_viewer").boldReportViewer({
        reportServerUrl:window.setting.server_report_url,
        reportServiceUrl: window.setting.report_service_url,
        reportPath: selectedReport.value.server_report_path,
        serviceAuthorizationToken: "bearer " + window.setting.embed_code,
        parameters: report_params,
        printMode:true,
        zoomFactor: 1.25,
        enableViewState: true,  // Enables the Save View feature
    toolbarSettings: {
        items: ej.ReportViewer.ToolbarItems.All,
        showSaveView: true,  // Shows Save View button on the toolbar
        showViewList: true,  // Enables selecting a saved view
    },
        reportLoaded: function(event) {
            setTimeout(() => {
                let property  = document.querySelector("#main_server_report_viewer_Param_101")
             
            }, 5000);
          
        }
    });
} 

function get_date_by_timestamp(timestap){

    if (timestap === "current_working_date") {
        return window.current_working_date;
    } else if (timestap === "today") {
        return moment().format("YYYY-MM-DD");
    } else if (timestap === "previous_working_day") {
        return moment(window.current_working_date).add(-1, "days").format("YYYY-MM-DD");
    } else if (timestap === "start_mtd") {
        return moment(window.current_working_date).startOf("month").format("YYYY-MM-DD");
    } else if (timestap === "end_mtd") {
        return moment(window.current_working_date).endOf("month").format("YYYY-MM-DD");
    } else if (timestap === "start_current_mtd") {
        return moment().startOf("month").format("YYYY-MM-DD");
    } else if (timestap === "end_current_mtd") {
        return moment().endOf("month").format("YYYY-MM-DD");
    }  else if (timestap === "start_ytd") {
        return moment(window.current_working_date).startOf("year").format("YYYY-MM-DD");
    } else if (timestap === "end_ytd") {
        return moment(window.current_working_date).endOf("year").format("YYYY-MM-DD");
    } else {
        return window.current_working_date;
    }
}
 
 

onMounted(() => {
    
});

onUnmounted(() => {
    
})


</script> 
<style scoped>
 /* Center form with better spacing */
.form-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Styling for the title */
.form-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: bold;
}

/* Styling for the button */
.save-button {
  margin-top: 20px;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
}

</style>
