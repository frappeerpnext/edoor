<template>
    <TabView>
        <TabPanel header="General Information">
            <iframe style="height:500px;width: 100%;"
                :src="generalInfoUrl">

            </iframe>

        </TabPanel>
        <TabPanel header="Stay History">
            <iframe style="height:500px;width: 100%;"
                src="http://192.168.10.114:1216/printview?doctype=Customer&name=C2022-0007&format=eDoor%20Guest%20Stay%20History&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0">

            </iframe>

        </TabPanel>

    </TabView>
</template>
<script setup>
import { inject, ref, onMounted,computed } from '@/plugin'
const dialogRef = inject("dialogRef");

const name = ref("")

const generalInfoUrl =  computed(() => {
    let url = "http://192.168.10.114:1216/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20Detail%20General%20Information&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
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