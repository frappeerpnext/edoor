<template>
    <TabView  lazy>
        <TabPanel header="General Information">
            <div class="iframe-view">
            <iframe style="height:500px;width: 100%;"
                :src="generalInfoUrl">
            </iframe>
            </div>
        </TabPanel>
        <TabPanel header="Stay History">
            <div class="iframe-view">
            <iframe  style="height:500px;width: 100%;"
                :src="stayHistoryUrl">
            </iframe>
            </div>
        </TabPanel>
        <TabPanel header="POS/Misc. Sale">
            <div class="iframe-view">
            <iframe style="height:500px;width: 100%;"
                :src="posMiscSaleUrl">

            </iframe>
            </div>
        </TabPanel>

        <TabPanel header="Note">
            <div class="iframe-view">
            <iframe style="height:500px;width: 100%;"
                :src="noteUrl">

            </iframe>
            </div>
        </TabPanel>
        <TabPanel header="Folio">
            <div class="iframe-view">
            <iframe style="height:500px;width: 100%;"
                :src="folioUrl">

            </iframe>
            </div>
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
const folioUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Reservation%20Folio&no_letterhead=1&letterhead=Defualt%20Letter%20Head&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})


onMounted(() => {
    if (dialogRef.value) {
        name.value = dialogRef.value.data.name;
    } else {
        alert(111)
    }
});

console.log(dialogRef)
</script>
<style scoped>
.iframe-view{
    margin-right: -1rem;
}
</style>