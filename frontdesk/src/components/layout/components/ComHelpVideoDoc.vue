<template>
     <InputText  class="w-full mb-2" v-model="keyword" placeholder="Search" @input="onSearch"  />
    <Accordion :multiple="true" :activeIndex="[0]">
       
                        <AccordionTab :header="$t('Quick Overview')">
                            <div class="grid p-4">
                                <div v-for="v in filterdata.filter(i => i.show_in_overview == 1)" :key="v.video_name" class="col-4 p-2">
                                    
                                 <a  :href="v.link" target="_blank"  class="item-youtube-hover px-3 py-2 shadow-1 font-semibold border-round-lg w-full inline-block border-bottom-1 border-red-300 flex align-items-center">
<span class="me-4"><ComIcon icon="youtube" height="25px" /></span>

                                    {{ v.video_name }}
                                 </a>
                                </div>
                           </div>
                        </AccordionTab>
                        <AccordionTab v-for="d in  filterdata.filter(i => i.is_group == 1)"  :key="d.video_name" :header="d.video_name" >
                           <div class="grid p-4">
                                <div v-for="v in filterdata.filter(i => i.parent_help_video_documentation == d.video_name)" :key="v.video_name" class="col-4 p-2">
                                    
                                 <a  :href="v.link" target="_blank"  class="item-youtube-hover px-3 py-2 shadow-1 font-semibold border-round-lg w-full inline-block border-bottom-1 border-red-300 flex align-items-center">
<span class="me-4"><ComIcon icon="youtube" height="25px" /></span>

                                    {{ v.video_name }}
                                 </a>
                                </div>
                           </div>
                        </AccordionTab>
                      
    </Accordion>
</template>
<script setup>
import { ref, getDocList, onMounted} from '@/plugin'
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ComIcon from '../../ComIcon.vue';

const data = ref([]);
const filterdata = ref([]);
const keyword = ref()
const loglang = ref()
const title = ref()

function loadData() {
    let filters = []
    getDocList('Help Video Documentation', {
        fields: ['parent_help_video_documentation', 'is_group', 'label','video_name','link','show_in_overview'],
        filters: filters,
        limit: 10000,
    })
    .then((doc) => {
        data.value = doc
        filterdata.value = doc
    })
    .catch((error) => {

    });    
}
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
    if (keyword.value != '') {
        filterdata.value = data.value.filter(i => 
    i.is_group == 1 || 
    i.video_name.toLowerCase().includes(String(keyword.value).toLowerCase())
);

    }else{
        filterdata.value =  data.value
    }
  


}, 500);
onMounted(() => {
    loadData()
    
})
</script>