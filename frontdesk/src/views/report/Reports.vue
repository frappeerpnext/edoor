<template>
    <div class="grid wrapper-report">
        <div class="col flex gap-2 mt-2">
            <div class="mt-2" v-if="isMobile">
                <Button icon="pi pi-bars" @click="visible = true" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"/>
            </div>
            <div class="text-2xl pt-3 lg:pt-2">Reports</div>
            <div class="col flex gap-2 justify-end ">
                <div v-if="(view||'')!='ui'">
                    <ComPrintButton :url="url"  @click="onPrint"/>
                </div>  
                <!-- <div v-if="!isMobile">
                    <Button @click="loadIframe" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                </div> -->
            </div>
        </div>
    </div>  

    <template v-if="isMobile">
        <Sidebar class="sidebar-report" v-model:visible="visible" header="Reports List">
            <ComReportTree @onTabClick="onTabClick" @onSelectReport="onSelectReport" />
        </Sidebar> 
        <div v-if="selectedReport" class="p-2">
            <div class="wrapp-filter-report"> 
                <ComReportFilter @onFilter="onFilter" @onGetHeight="onGetHeight" :selectedReport="selectedReport" />
            </div>
            <iframe @load="onIframeLoaded()" id="iframe" width="100%" :src="url"></iframe>
        </div>
        <div v-else class="p-2 flex align-items-center h-100 justify-center">
            <p class="text-center text-2xl pt-3">Please select a report from Sidebar.</p>
        </div>
    </template>
    <template v-else>
        <Splitter class="mb-5" state-key="report_spliter_state" state-storage="local">
            <SplitterPanel :size="25" class="pa-4 left-side-panel overflow-y-auto">
                <ComReportTree @onTabClick="onTabClick" @onSelectReport="onSelectReport" />
            </SplitterPanel>

            <SplitterPanel :size="75" class="pa-4">
                <div v-if="selectedReport" class="p-2">
                    <div class="wrapp-filter-report"> 
                        <ComReportFilter @onFilter="onFilter" @onGetHeight="onGetHeight" :selectedReport="selectedReport" />
                    </div>
                    <iframe @load="onIframeLoaded()" id="iframe" width="100%" :src="url"></iframe>
                </div>
                <div v-else class="p-2 flex align-items-center h-100 justify-center">
                    <p class="text-center text-2xl pt-3">Please select a report on the left bar.</p>
                </div>
            </SplitterPanel>
        </Splitter>
    </template>
</template>
<script setup>
import { ref, onMounted, inject,onUnmounted } from "@/plugin"
import ComReportTree from "@/views/report/components/ComReportTree.vue"
import ComReportFilter from "@/views/report/components/ComReportFilter.vue"
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';

const isMobile = ref(window.isMobile) 
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol=="http:"?"http://" + window.location.hostname + ":" + window.setting.backend_port:"https://" + window.location.hostname;
const url = ref("")
const gv = inject("$gv")

const visible = ref(false)

const selectedReport = ref()
const filters = ref({})

function onGetHeight(f) { 
    setIframeHeight(f.value)
}

function onSelectReport(p) { 
    selectedReport.value = p
    setTimeout(function(){ 
        if (selectedReport.value){
            loadIframe()
        }
    }, 100)
}
function onFilter(f) {
    
    if (selectedReport.value) {
        filters.value = f 

        loadIframe()
    }

}

function onTabClick (){
    const bodyHeight = document.querySelector('body').clientHeight
    const headerBar = document.querySelector('.header-bar').clientHeight 
    const footerHeight = document.querySelector('.wrapper-foot-deco').clientHeight 
    const wrapperReport = document.querySelector('.wrapper-report').clientHeight

    const leftSideBar = bodyHeight - (headerBar + footerHeight + wrapperReport + 17)
    if (document.querySelector('.left-side-panel')){
        document.querySelector('.left-side-panel').style.height = leftSideBar + 'px'
    }
}

function onIframeLoaded() {
    const iframe = document.getElementById("iframe");
    if (iframe.contentWindow.document.body.scrollWidth < iframe.offsetWidth) {
        iframe.style.overflowX = 'hidden';
    } else {
        iframe.style.overflowX = 'auto';
    }
 
}

const setIframeHeight = (f) => { 
    let filterHeight = 0
    const wrapperFilterReport = document.querySelector('.wrapp-filter-report').clientHeight
    const bodyHeight = document.querySelector('body').clientHeight
    const headerBar = document.querySelector('.header-bar').clientHeight
    const wrapperReport = document.querySelector('.wrapper-report').clientHeight
    const footerHeight = document.querySelector('.wrapper-foot-deco').clientHeight 
    if (f == undefined) {
        filterHeight = wrapperFilterReport
    }else if (f == true){
        filterHeight = 153
    }else if(f == false){
        filterHeight = 20
    }  
    const iframeHeight = bodyHeight - (headerBar + wrapperReport + filterHeight + footerHeight + 30)
    const sidePanelHeight = bodyHeight - (headerBar + wrapperReport + footerHeight + 30)
    document.querySelector('#iframe').style.height = iframeHeight + 'px' 
    if (document.querySelector('.left-side-panel')){
        document.querySelector('.left-side-panel').style.height = sidePanelHeight + 'px'
    }
}

function loadIframe() {

    if (selectedReport.value) {
        url.value = serverUrl + "/printview?doctype=Business%20Branch&name=" + setting.property.name + "&format=" + gv.getCustomPrintFormat(selectedReport.value.report_name) + "&&settings=%7B%7D&show_toolbar=0"


        if (Object.keys(filters.value)) {
            Object.keys(filters.value).forEach(p => {
                if (filters.value[p]) {
                    url.value = url.value + "&" + p + "=" + filters.value[p]
                }
            });
        }

        url.value = url.value + "&refresh=" + (Math.random() * 16)
        
         
        document.getElementById("iframe").contentWindow.location.replace(url.value)

        setIframeHeight()
         
    }

}
function onPrint(){
    document.getElementById("iframe").contentWindow.print()
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="Reports"){
            setTimeout(()=>{
                loadIframe()
            },1000*3)
            
        }
    };
}

onMounted(() => {
    loadIframe() 
    window.addEventListener('message', actionRefreshData, false)
});

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false)
})


</script> 
<style scoped>
.full-height {
    height: 90vh;
}
</style>