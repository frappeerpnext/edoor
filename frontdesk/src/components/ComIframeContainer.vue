<template>
<template v-if="pageName">
<div class="grid bg-white p-2">
    <div class="col-2 ps-2 border-r-2">
        <div :class="m.route == active ? 'active_class_route' : ''" class="border-1 border-round-lg p-2 mt-2 cursor-pointer" v-for="(m, index) in subMenus"  :key="index" @click="ReloadIframe(m)" >
 <a >{{ m.title }}</a>
        </div>
        <div class="card flex justify-center">
    </div>
    </div>
<div class="col-10">
    <iframe  id="iframe-page-container" :src="url" style="width: 100%;"></iframe>
</div>
    
</div>
    

</template>
<template v-else>
    <iframe  id="iframe-page-container" :src="url" style="width: 100%;"></iframe>
</template>

</template>

<script setup>
import { inject, ref,  getDoc, onMounted } from '@/plugin'

import PanelMenu from 'primevue/panelmenu';

const active = ref();
const props = defineProps({
   pageName:String,
   defaultFilter:String,
   iframeUrl:String
})
const url=ref("")
const loading = ref(true)
const subMenus = ref([])
function ReloadIframe(menu){
    const iframe = document.querySelector('#iframe-page-container');
    if (iframe){
        iframe.style.height =  '100px';
    }
    
    active.value = menu.route
    url.value = menu.route + "?refresh=" + (Math.random() * 16)
    if (props.defaultFilter){
            url.value = url.value + "&" + props.defaultFilter 
        }
}
onMounted(() => {
    if (props.pageName) {
    loading.value = true
    getDoc("Iframe Page",props.pageName).then(doc=>{
        url.value = doc.route 
        active.value = doc.route 
        if (props.defaultFilter){
            url.value = url.value + "?" + props.defaultFilter 
        }
        subMenus.value = doc.sub_menus
        loading.value = false

        setIframeHeight()
        

    }).catch(error=>{
        loading.value = false
    })
    }else {
        url.value = props.iframeUrl
        setIframeHeight()
    }
    
})

function setIframeHeight () {

    const iframe = document.querySelector('#iframe-page-container');
         
    if (iframe){
        iframe.style.minHeight = ( window.innerHeight) +  "px"
    }

    iframe.addEventListener('load', function () {
        var observer = new MutationObserver(function (mutationsList) {
            iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';

        });

        // Observe changes to the body of the document inside the iframe
        observer.observe(iframe.contentWindow.document.body, { attributes: true, childList: true, subtree: true });
    });
}
</script> 