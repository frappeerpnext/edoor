<template>
    <ComDialogContent @onOK="onOk" hideButtonClose :loading="loading" titleButtonOK="Save Setting" :hideIcon="false" >
<div v-if="setting" class="grid">
        <div>
        <Card class="border-round-xl surface-50 shadow-1 mb-3">
            <template #title>Show Columns Date View </template>
            <template #content>
                <div class="grid">
                    <div class="col-6 py-1 flex" v-for="(d, index) in reportConfig?.report_fields" :key="index">
                            <Checkbox v-model="setting.show_columns" :inputId="'show_column_' + d.fieldname"  :value="d.fieldname"/>
                            <label :for="'show_column_' + d.fieldname"  class="ml-2"> {{ d.label }}</label>
                    </div>
                </div>
            </template>
        </Card>
    </div>
    <div>
        <Card class="border-round-xl surface-50 shadow-1 mb-3">
        <template #title>
        <div class="flex items-center">
            <Checkbox v-model="setting.show_summary" inputId="show_summary_kpi"  :binary="true" :trueValue="1" :falseValue="0" />
            <label for="show_summary_kpi"  class="ml-2 ms-4"> Summary KPI</label>
        </div>
        </template>
        <template #content>
        
            <div  class="grid -mt-2 ">
        <div class="col-6 py-1 flex" v-for="(d, index) in reportConfig?.report_fields?.filter((y) => y.show_in_chart == 1)" :key="index">
            <Checkbox :disabled="!setting.show_summary" v-model="setting.show_summary_field" :inputId="'show_summary_' + d.fieldname"  :value="d.fieldname"/>
            <label :for="'show_summary_' + d.fieldname"  class="ml-2"> {{ d.label }}</label>
            </div>
        
        </div>

        </template>
    </Card>
    </div>
    <div>
        <Card class="border-round-xl surface-50 shadow-1 mb-3">
        <template #title>Chart</template>
        <template #content>
        <div class="grid -mt-5">
            <div class="col-12">
            <span class="font-bold">Chart Type</span>
            <ComSelect :clear="false" :options="chartTypeOption" v-model="setting.chart_type"/> 
            </div>
            <div class="col-12">
    <span class="font-bold">Chart Series</span>
    <div class="grid mt-2">
    <div class="col-6 flex py-1" v-for="(d, index) in reportConfig?.report_fields?.filter((y) => y.show_in_chart == 1)" :key="index">
            <Checkbox v-model="setting.show_chart_series" :inputId="'chart_series_' + d.fieldname"  :value="d.fieldname"/>
            <label :for="'chart_series_' + d.fieldname"  class="ml-2"> {{ d.label }}</label>
        </div>
    </div>
    
            </div>
        </div>
        </template>
    </Card>
    </div>
</div>

    <!-- {{ reportConfig }} -->
    
   

 

</ComDialogContent>
</template>
<script setup>
    import {ref,inject,onMounted,getApi} from "@/plugin"
    import BlockUI from 'primevue/blockui';
import { Loading, resultProps } from "@varlet/ui";
const loading = ref(false) 
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
        loading.value = true
        getApi("utils.get_report_config",{
            property:window.property_name,
            report:"Revenue and Occupancy Summary Report"
        }).then(result=>{
            loading.value = false
            reportConfig.value = result.message
        })
    })
</script>