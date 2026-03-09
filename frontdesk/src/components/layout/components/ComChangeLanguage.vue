<template>
    <div class="w-full">
        <div>
            <div class="p-input-icon-left w-full">
                            <i class="pi pi-search" />
                            <InputText  class="w-full" v-model="keyword" placeholder="Search" @input="onSearch"  />
                        </div>
                        <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="languages.length > 0">                
        <div class="flex w-full mt-2" v-for="(language, index) in languages" :key="index">
            <Button class="w-full" :class="(loglang === language.name) ? 'bg-green-200' : ''" @click="onChangeLanguage(language.name)" severity="secondary" raised text >
                <div style="padding:2px;" class="surface-ground border-round-sm">
 <img style="width:30px;" class="border-round-sm" :src="language.flag" /> 
                </div>
            <p class="ms-3 text-color">{{ language.language_name }}</p>
            </Button>   
        </div>
        </ComPlaceholder>
       </div>
    </div>
</template>
<script setup>
import { ref, getDocList, onMounted} from '@/plugin'
const languages = ref([])
const keyword = ref()
const loglang = ref()
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
    loadData()
}, 500);

function onChangeLanguage(lang){
    localStorage.setItem("lang",lang)
        window.location.reload();
}
function loadData() {
    let filters = []
    if (keyword.value) {
        filters.push(["language_name", "like", '%' + keyword.value + '%'])
    }
    getDocList('POS Translation', {
        fields: ['language_name', 'flag', 'name'],
        filters: filters,
        limit: 10000,
    })
    .then((doc) => {
        languages.value = doc
    })
    .catch((error) => {

    });    
}
onMounted(() => {
    loadData()
    loglang.value = localStorage.getItem("lang") || "en";
})
</script>