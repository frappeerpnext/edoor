<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Save Setting" :hideIcon="false" >
    {{ setting }}
        <h1>Show Columns</h1>
        <h1>Show Columns</h1>
      <div class="flex items-center" v-for="(d, index) in reportConfig?.report_fields" :key="index">
        <Checkbox v-model="setting.show_columns" :inputId="'show_column_' + d.fieldname"  :value="d.fieldname"/>
        <label :for="'show_column_' + d.fieldname"  class="ml-2"> {{ d.label }}</label>
    </div>
    <hr>
    
    <h1>Show Summary</h1>

    <div class="flex items-center">
        <Checkbox v-model="setting.show_summary" inputId="show_summary"  :binary="true" :trueValue="1" :falseValue="0" />
        <label for="show_summary" class="ml-2"> Show Summary KPI </label>
    </div>
    <h1>Show Summary Field</h1>
    <div class="flex items-center" v-for="(d, index) in reportConfig?.report_fields?.filter((y) => y.show_in_chart == 1)" :key="index">
        <Checkbox v-model="setting.show_summary_field" :inputId="'show_summary_' + d.fieldname"  :value="d.fieldname"/>
        <label :for="'show_summary_' + d.fieldname"  class="ml-2"> {{ d.label }}</label>
    </div>
    <hr>

    <h1>View Chart Type</h1>
    <ComSelect :clear="false" :options="chartTypeOption" v-model="setting.chart_type"/>
    <!-- {{ reportConfig }} -->
    
    <h1>Chart Series</h1>
    <div class="flex items-center" v-for="(d, index) in reportConfig?.report_fields?.filter((y) => y.show_in_chart == 1)" :key="index">
        <Checkbox v-model="setting.show_chart_series" :inputId="'chart_series_' + d.fieldname"  :value="d.fieldname"/>
        <label :for="'chart_series_' + d.fieldname"  class="ml-2"> {{ d.label }}</label>
    </div>

 

</ComDialogContent>
</template>
<script setup>
    import {ref,inject,onMounted,getApi} from "@/plugin"
import { resultProps } from "@varlet/ui";
 
    const dialogRef = inject("dialogRef");
    const reportConfig = ref({})
    const setting = ref({
        "chart_type":"bar"
    })
    const chartTypeOption = ref(["None","bar","line"])

    function onOk(){
        localStorage.setItem("frontdesk_map_view_setting", JSON.stringify(setting.value))
        dialogRef.value.close(setting.value);
    }
    onMounted(()=>{
        const s = localStorage.getItem("frontdesk_map_view_setting")
        if (s){
            setting.value = JSON.parse(s)
        }
        getApi("utils.get_report_config",{
            property:window.property_name,
            report:"Revenue and Occupancy Summary Report"
        }).then(result=>{
            reportConfig.value = result.message
        })
    })
</script>