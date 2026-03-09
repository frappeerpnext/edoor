<template>

    <div class="p-2">
        <div class="mb-3">
          
            <InputText class="w-full" v-model="keyword" @input="onSearch" :placeholder="$t('Search Report (min. 3 characters)')" />
        </div>
        <div v-if="!loading">
        
            <PanelMenu  :model="reportItems" class="w-full">
                
                <template #item="{ item }"> 
                    <a v-ripple class="flex align-items-center px-3 py-2 cursor-pointer" :class="[selectedReport?.name == item.name ? 'bg-blue-100': '',item.items.length>0 ? 'bg-gray-50 border-2': 'mx-2 border-1 border-round-md my-1' , item?.parent_system_report != rootReport.value , '' , 'mx-2 border-1 border-round-md my-1']" >
                        
                        <span :class="['pi pi-angle-right', 'text-primary']" v-if="item.items.length>0" />
                        <span :class="['ml-2', { 'font-semibold': item.items }]">{{ item.report_title }} 
                        </span>
                        <Badge  class="ml-auto" :value="item.items.length" v-if="item.items.length>0" />
                    </a>

    </template>
            </PanelMenu>
        </div>
    </div>

   

</template>
<script setup>
import { ref, getDocList, onMounted, computed } from "@/plugin"
import { useRoute } from 'vue-router';
import {i18n} from '@/i18n';
const props = defineProps({
    root_report:String
})
const { t: $t } = i18n.global;
const emit = defineEmits(["onSelectReport","onTabClick"])
const selectedReport = ref()
import PanelMenu from 'primevue/panelmenu';
import { watch } from "vue";
 
const keyword = ref("")
const loading = ref(false)
const reportItems = ref([])
const allReports =ref([]) 
const filterReports =ref([]) 


const rootReport = computed(() => {
    return props.root_report === "ServerReports" ? "eDoor Report" : "POS Report";
});

watch(() => props.root_report, (newValue, oldValue) => {
  
    reportItems.value = buildTreeData();
});


const onSearch = debouncer(() => {
    if (keyword.value) {
        if(keyword.value.length>=3){
       // get all parent
       filterReports.value = allReports.value.filter(r=>r.is_group == 1)
        // get all child that match with fitler
        filterReports.value = [...filterReports.value,...allReports.value.filter(r=>r.is_group == 0 && (r.report_title?.toLowerCase() + " " +  r.keyword?.toLowerCase()).includes(keyword.value.toLowerCase()))]

        }
 
    } else {
        filterReports.value =  allReports.value
        
    }
    reportItems.value = buildTreeData()
   
   
}, 700);



function debouncer(fn, delay) {
  var timeoutID = null;
  return function () {
    clearTimeout(timeoutID);
    var args = arguments;
    var that = this;
    timeoutID = setTimeout(function () {
      fn.apply(that, args);
    }, delay);
  };
}
 
 


function onTabClick () {
    emit("onTabClick")
}


function buildTreeData(){
 
    if(filterReports.value){
        let tree_report_data = filterReports.value.filter(r=>r.parent_system_report == rootReport.value  );
    tree_report_data.forEach(parent=>{
        parent.keyword  = parent.report_title 
        parent.items = getSubReportItem(parent)
    })
    if (keyword.value){
        
        return    tree_report_data.filter(r=>r.items.length>0)
         
    }else {
        return tree_report_data;
    }
   
}

   return []
    

}

function getSubReportItem(parent){
    
    let child_report_items = filterReports.value.filter(r=>r.parent_system_report==parent.name);
    child_report_items.forEach(ch =>{
        ch.items = getSubReportItem(ch);
        ch.keyword = parent.keyword + " " + ch.report_title
        if (ch.items.length==0 && ch.is_group == 0){
            ch.command= () => {
                selectedReport.value = ch;
                emit("onSelectReport",ch);
                }
        }

    })
    return  child_report_items;
}

onMounted(() => {
    loading.value = true;
    getDocList("System Report", {
        fields: ["name", "is_group", "report_title", "report_name","server_report_path", "filter_option", "parent_system_report","filter_default_value"],
        orderBy: {
            field: "sort_order",
            order: "asc"
        },
        limit: 1000,
    }).then((result) => {
        const translatedResults = result.map(item => ({
        ...item,
        report_title: $t(item.report_title),
      }));
        allReports.value = translatedResults
        filterReports.value = translatedResults;
        
         reportItems.value = buildTreeData();
        loading.value = false;
    }).catch((err) => {
        loading.value = false;
    })

})

</script>
<style scoped>
.p-panelmenu .p-panelmenu-content .p-menuitem:not(.p-highlight):not(.p-disabled)>.p-menuitem-content:hover{
    background: none !;
}
</style>