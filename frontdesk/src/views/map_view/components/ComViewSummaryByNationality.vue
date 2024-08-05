<template>
    <ComDialogContent  hideButtonClose titleButtonOK="Ok" :hideIcon="false" :loading="loading" > 
    <div class="grid gap-2">
<Button :class="{ 'active_btn': activeIndex === index }" class="conten-btn" v-for="(view_type, index) in displayBy" :key="index" @click="onLoadData(view_type,index)">{{ view_type }}</Button>
    </div>
      
    <hr class="my-2">
    <div class="mt-2">
       <ComSummaryKPI :report_summary ="data?.report_summary" bgColor="surface-100"/>
    </div>
   

    <ComChartView v-if="data?.chart" :chart="data?.chart"/>

    <hr>
    <ComViewDataInTable :data="data?.result" :columns="data?.columns" />
</ComDialogContent>
</template>
<script setup>
    import {ref,inject,onMounted,nextTick,getApi} from "@/plugin"
    import {i18n} from '@/i18n';
    import { useDialog } from 'primevue/usedialog';
    import ComSummaryKPI from "@/views/map_view/components/ComSummaryKPI.vue"
    import ComViewDataInTable from "@/views/map_view/components/ComViewDataInTable.vue"
    import ComChartView from "@/views/map_view/components/ComChartView.vue"
    const activeIndex = ref(0);
    const { t: $t } = i18n.global;
    const dialog = useDialog()
    const moment = inject("$moment")
    const dialogRef = inject("dialogRef");
    const displayBy =["Date","Month","Year", "Room Type","Room", "Business Source","Business Source Type","Guest Type"]
    const filters = ref()
    const defaultFilter = "Month"
    const data = ref()
    const loading = ref(true)

async function onLoadData(view_type=defaultFilter,index) {
  activeIndex.value = index;
  await nextTick();
  if (filters.value.timespan=="Date Range"){
    if (!filters.value.start_date || !filters.value.end_date){
      return
    }
  }

  loading.value = true
  filters.value.row_group = view_type
  getApi(
    "frappe.desk.query_report.run",
    {
      report_name: "Revenue and Occupancy Summary Report",
      filters:filters.value,
      ignore_prepared_report: false,
      are_default_filters: false,
    },
    ""
  ).then((result) => {
    data.value = result.message;
    loading.value= false ;
  }).catch(error=>{
    loading.value= false ;
  });
  
}
    onMounted(()=>{
        
        filters.value = dialogRef.value.data.filters
        
        const defaultIndex = displayBy.indexOf(defaultFilter);
  if (defaultIndex !== -1) {
    onLoadData(defaultFilter, defaultIndex);
  }
    })

</script>