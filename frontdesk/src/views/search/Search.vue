<template >
 <ComDialogContent   hideButtonOK :hideButtonClose="true"  >
   
        <div class="d-flex w-full">
            <span class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText class="w-full unrounded__box_cus bg-transparent" v-model="keyword" placeholder="Search"
                    @input="onSearch" autofocus />
            </span>
        </div>


        <Button v-for="(d, index) in search_table" :key="index" @click="onSelectTable(d)">{{ d.title }} {{ d.selected
        }}</Button>


        <div v-if="!keyword">Please enter few keyword to search data from database</div>
        <template v-else>
            <div v-if="loading">Loading...</div>
            <div v-else>
               
                <Listbox v-model="selectedDoctype" :options="resultDoctypes" class="w-full md:w-14rem">
                    <template #option="slotProps">
                        <div class="flex align-items-center">
                            <div>{{ search_table.find(r => r.doctype == slotProps.option.doctype).title }} ({{
                                results.filter(r => r.doctype == slotProps.option.doctype).length }})
                            </div>
                        </div>
                    </template>
                </Listbox>

                <hr />
                <DataView :value="results.filter(r=>r.doctype ==(selectedDoctype?.doctype || r.doctype))" paginator :rows="20">
                    <template #list="slotProps">
                        <div class="col-12">
                            <div class="flex flex-column xl:flex-row xl:align-items-start p-4 gap-4">
                                <div v-html="getTemplate(slotProps.data)"></div>
                                <Button v-if="slotProps.data.action_name" @click="onViewDetail(slotProps.data)">View
                                    Detail</Button>
                            </div>
                        </div>

                    </template>
                </DataView>

           
            

            </div>
        </template>



    </ComDialogContent>
</template>
<script setup>
import { getApi, ref, postApi, computed } from "@/plugin"
import Mustache from 'mustache';
import ComDialogContent from '../../components/form/ComDialogContent.vue';
import DataView from 'primevue/dataview';
const results = ref([])
const loading = ref(false)
const keyword = ref("")
const search_table = ref(window.setting.search_table)
const resultDoctypes = ref()
const selectedDoctype = ref("")

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
    loadData();
}, 500);



function loadData() {

    if (keyword.value) {
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
    } else {
        results.value = []
    }
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

    let table = window.setting.search_table.find(r => r.doctype == d.doctype)

    return renderTemplate(table.template, d);
}

</script>
<style ></style>