<template>
    <SplitButton :class="BtnClassPrinter ? BtnClassPrinter : 'spl__btn_cs_b sp_b'" @click="onPrint" id="btnprint" :label="$t('Print')" icon="pi pi-print" :model="items" />
 
</template>
<script setup>
const emit = defineEmits(["click"])
const props = defineProps({
    url:String,
    BtnClassPrinter:String
})
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const items = [
    {
        label: $t('Export PDF (Portrait)'),
        icon: 'pi pi-file-pdf',
        command: () => {
            const url = props.url.replace("printview","api/method/frappe.utils.print_format.download_pdf") + "&orientation=Portrait" 
              window.open(url, "newWindow", "width=1000,height=1000");
           
        }
    },
    {
        label: $t('Export PDF (Landscape)'),
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
