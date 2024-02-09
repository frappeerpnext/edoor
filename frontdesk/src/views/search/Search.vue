<template >
 <ComDialogContent   hideButtonOK :hideButtonClose="true"  >
 <div class="grid"> 
    <div class="col-12">
        <div class="d-flex w-full">
            <span class="p-input-icon-left  w-full">
                <i class="pi pi-search" />
                <InputText class="w-full unrounded__box_cus bg-transparent" v-model="keyword" placeholder="Search"
                    @input="onSearch" autofocus />
                <Button @click="onShowFilter()" icon="pi pi-sliders-h" class="absolute right-2" :class="ShowFilterSearch ? 'text-blue-400' :''" aria-label="Filter" link />
            </span>
        </div>
</div>
<hr class="mt-2">
<div v-if="ShowFilterSearch" class="col-12">

<div class="grid gap-2">
  <Button class="border-1 bg-transparent border-round-3xl text-md box-shadow-box-search white-space-nowrap" :class="d.selected ? 'text-blue-400':'border-500 text-color'" v-for="(d, index) in search_table" :key="index" @click="onSelectTable(d)">{{ d.title }}
<i v-if="d.selected" class="pi pi-check ms-3"></i>    

</Button>
</div>
</div>     
<div class="col-12">
<hr class="drop-shadow-md">

        <div class="flex justify-center mt-4" v-if="!keyword && results.length==0">
            "
            <i class="pi pi-search text-yellow-200 text-2xl mx-2" />
            "
            <span class="text-md ms-4">
            Please enter few keyword to search data from database   
            </span>
        </div>
        <template v-else>
            <div>
                <ComPlaceholder :text="'No Data With  `  ' + keyword + '  `  Keyword'" :loading="loading" :is-not-empty="results.filter(r=>r.doctype ==(selectedDoctype?.doctype || r.doctype) ).length > 0">
               <div class="grid pt-2">
                <div class="md:col-2 hidden md:block col-12 bg-card-info p-0">
                <Listbox filtericon="HI" v-model="selectedDoctype" :options="resultDoctypes" class="w-full bg-transparent p-2">
                    <template  #option="slotProps">
                        <div class="flex align-items-center justify-between">
                            <div>{{ search_table.find(r => r.doctype == slotProps.option.doctype).title }}
                            </div>
                            <Badge class="surface-200 text-color" :value="results.filter(r => r.doctype == slotProps.option.doctype).length"></Badge>
                        </div>
                    </template>
                </Listbox>
                </div>
                <div class="md:col-10 col-12 p-0 search_style_section">     
                <DataView @page="pagechange()" :first="first" :value="results.filter(r => r.doctype === (selectedDoctype?.doctype || r.doctype))" paginator :rows="20">
                
                    <template #list="slotProps">
                        
                        <div v-for="(data, index) in slotProps.items" :key="index" class="col-12 search-hover relative" id="contentContainer">
                            <div class="">
                                <div v-html="getTemplate(data)"></div>
                               <span>
                                <div class="text-500 text-md absolute bottom-5 right-10">
                                    {{ data && data.modified_by && typeof data?.modified_by === 'string' ? data.modified_by.split('@')[0] : '' }}  -  <ComTimeago :date="data?.modified"></ComTimeago>
</div>                    
                               </span>
                            </div>
                        </div>
                    </template>
                </DataView>
                        </div>
                </div>
            </ComPlaceholder>
            </div>

        </template>
    
    </div>

    </div> 
    </ComDialogContent>
</template>
<script setup>
import { getApi, ref, postApi, computed , onMounted , onUnmounted } from "@/plugin"
import Mustache from 'mustache';

import ComDialogContent from '@/components/form/ComDialogContent.vue';
import DataView from 'primevue/dataview';
const ShowFilterSearch = ref(true)
function onShowFilter() {
    ShowFilterSearch.value = !ShowFilterSearch.value
    localStorage.setItem("edoor_show_filter_search", ShowFilterSearch.value ? "1" : "0")
}

const results = ref([])
const loading = ref(false)
const keyword = ref("")
const search_table = ref(window.setting.search_table)
const resultDoctypes = ref()
const selectedDoctype = ref("")
const first = ref(0)

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
const onSearch = debouncer(() => {
    first.value = 0
    loadData();

}, 500);



function loadData() {

 
        loading.value = true
        postApi("frontdesk.search", { doctypes: getSearchTable(), txt: keyword.value }, '', false)
            .then(result => {
                results.value = result.message
                const doctypes = [...new Set(results.value.map(r => r.doctype))]
                resultDoctypes.value = []
                doctypes.forEach(r => {

                    resultDoctypes.value.push({ doctype: r })
                })
                loading.value = false
            }).catch(err => {
                loading.value = false
            })
   
}

function onSelectTable(d) {
    d.selected = !d.selected
}


function onViewDetail(d) {
    if (d.action_name) {
        window.postMessage(d.action_name + '|' + d.name, '*')
    }
}

function getSearchTable() {
    if (search_table.value.filter(r => r.selected).length > 0) {
        return search_table.value.filter(r => r.selected).map(x => x.doctype)
    } else {
        return search_table.value.map(x => x.doctype)
    }
}

function renderTemplate(templateText, data) {
    var template = Mustache.render(templateText, data);
    return template;
}

function getTemplate(d) {
    if(d){
        let table = window.setting.search_table.find(r => r.doctype == d.doctype)

        return renderTemplate(table.template, d);
    }
    return ""
    
}
const scrollToTop = () => {
    const contentContainer = document.querySelector('.search_style_section');

 
  if (contentContainer) {
    contentContainer.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
};

function pagechange(){
    scrollToTop();
}

onUnmounted(()=>{
    window.open_search = false
    
})
onMounted(()=>{
    window.open_search = true
    loading.value = true
    loadData()
    
})
</script>
<style scoped>
::v-deep .p-listbox .p-listbox-list .p-listbox-item {
    background-color: white;
    margin: 6px 5px;
    border: 1px solid #7e6e6e;
    border-radius: 20px;
    box-shadow: rgba(0, 0, 0, 0.1) 0px 1px 2px 0px;
}
::v-deep .p-listbox .p-listbox-list .p-listbox-item.p-highlight{
    border-color: #609af8 !important;
    color: #609af8 !important;
}
::v-deep .p-highlight .p-badge{
    background-color: #609af8 !important;
    color: white !important;
}
</style>