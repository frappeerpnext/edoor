<template>
    <TabView  lazy>
        <TabPanel header="General Information">
            <iframe style="height:500px;width: 100%;"
                :src="generalInfoUrl">

            </iframe>

        </TabPanel>
        <TabPanel header="Stay History">
            <iframe style="height:500px;width: 100%;"
                :src="stayHistoryUrl">

            </iframe>

        </TabPanel>
        <TabPanel header="POS/Misc. Sale">
            <iframe style="height:500px;width: 100%;"
                :src="posMiscSaleUrl">

            </iframe>

        </TabPanel>

        <TabPanel header="Note">
            <iframe style="height:500px;width: 100%;"
                :src="noteUrl">

            </iframe>

        </TabPanel>
    </TabView>
</template>
<script setup>
import { inject, ref, onMounted,computed } from '@/plugin'
const dialogRef = inject("dialogRef");
const setting =JSON.parse( localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;

const name = ref("")
 

const generalInfoUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Detail%20General%20Information&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const stayHistoryUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Stay%20History&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const posMiscSaleUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20POS%2FMisc.%20Sale&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const noteUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Note&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})

onMounted(() => {
    if (!dialogRef) {
        alert(111)
    } else {
        name.value = dialogRef.value.data.name;
    }
});

console.log(dialogRef)
</script>