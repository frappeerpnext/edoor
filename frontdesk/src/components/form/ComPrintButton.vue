<template>
    <SplitButton class="spl__btn_cs sp" @click="onPrint" id="btnprint" label="Print" icon="pi pi-print" :model="items" />
 
</template>
<script setup>
const emit = defineEmits(["click"])
const props = defineProps({url:String})

const items = [
    {
        label: 'Export PDF (Portrait)',
        icon: 'pi pi-file-pdf',
        command: () => {
            const url = props.url.replace("printview","api/method/frappe.utils.print_format.download_pdf") + "&orientation=Portrait" 
              window.open(url, "newWindow", "width=1000,height=1000");
           
        }
    },
    {
        label: 'Export PDF (Landscape)',
        icon: 'pi pi-file-pdf',
        command: () => {
            const url = props.url.replace("printview","api/method/frappe.utils.print_format.download_pdf") + "&orientation=Landscape" 
              window.open(url, "newWindow", "width=1000,height=1000");
           
        }
    },
];


function onPrint(){
    emit("click")
}

</script>
