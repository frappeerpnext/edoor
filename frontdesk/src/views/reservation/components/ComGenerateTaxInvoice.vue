<template>
    <ComDialogContent :disabledBtnOk="!isConfirm"  @onOK="onSave" titleButtonOK="Ok" :loading="isSaving" hideButtonClose>
        <div class="grid">
        <div class="col-12">
<Message class="w-full p-0 m-0" severity="info">
    Please make sure that once generated, the Tax Invoice cannot be deleted or regenerated.
</Message>
        </div>
            
            <div class="col-12">
<label>{{$t('Tax Invoice Date')}}</label>
 <Calendar   class="p-inputtext-sm w-full"
                                    v-model="tax_invoice_date" :placeholder="$t('Tax Invoice Date')"
                                    dateFormat="dd-mm-yy" showIcon showButtonBar panelClass="no-btn-clear"
                                     />
            </div>
            <div class="col-12">
                <table class="w-full">
                    <ComStayInfoNoBox label="Current Tax Invoice" :value="data?.current_counter" />
                    <ComStayInfoNoBox label="Next Tax Invoice" :value="data?.next_tax_invoice_number" /> 
                </table>
                <div class="text-center shadow-1 p-3 mt-3 border-round-xl">
                        <div class="text-2xl">Rate Exchange</div>
                        <span class="text-2xl">
                            <CurrencyFormat currAddClass="font-semibold" :value="1" />({{ data?.base_currency }}) =
                            <CurrencyFormat currAddClass="font-semibold" :value="4000" :currency="data?.second_currency" /> ({{
                                data?.second_currency?.currency }})
                        </span>
                    </div>
            </div>
            <div class="col-12 flex justify-content-end">
           <Button class="conten-btn" @click="viewfoliotaxinvoicedetail()" label="Preview Before Generating" icon="pi pi-eye" />     
        </div>
        </div>
        
         
        <div class="relative mt-2">
            <span class="absolute w-full"><Checkbox class="w-full" v-model="isConfirm" :binary="true" /></span>
            <span class="pl-5">I am verify that all information is correct</span>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref,useConfirm, onMounted,getApi,postApi} from "@/plugin"
import {i18n} from '@/i18n';
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import { useDialog } from 'primevue/usedialog';
const dialog = useDialog();
const { t: $t } = i18n.global; 
const isConfirm = ref(false)
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const exchangeRates = ref()
const tax_invoice_date = ref(moment(window.current_working_date).toDate())
const data = ref()
const confirm = useConfirm()
const gv = inject("$gv")
function onSave() {
    confirm.require({
            message: $t('Are you sure you want to Generate Tax Invoice'),
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptIcon: 'pi pi-check-circle',
            acceptLabel: 'Ok',
            accept: () => {
                isSaving.value = true
    postApi("utils.generate_tax_invoice",{
        property:dialogRef.value.data.property,
        folio_number:dialogRef.value.data.name,
        tax_invoice_date:moment(tax_invoice_date.value).format("YYYY-MM-DD")
    }).then(result=>{
        isSaving.value = false
        dialogRef.value.close()
    }).catch(err=>{
        isSaving.value = false
    })
            },

        });
    
}
function viewfoliotaxinvoicedetail() {
     
     dialog.open(ComIFrameModal, {
         data: {
             doctype: "Reservation Folio",
             extra_params:[
				{key:'date',value: moment(tax_invoice_date.value).format("YYYY-MM-DD")},
			],
             name: dialogRef.value.data.name,
             report_name: gv.getCustomPrintFormat("Folio Tax Invoice Detail"),
             letterhead:"Tax Letterhead"
         },
         props: {
             header: $t("Print Tax Invoice"),
             style: {
                 width: '80vw',
             },
             position: "top",
             modal: true,
             maximizable: true,
             closeOnEscape: false,
             breakpoints:{
                 '960px': '80vw',
                 '640px': '100vw'
             },
         },
     });
 
 }
 function get_tax_invoice_info() {
    isSaving.value = true 
    getApi("utils.get_generate_tax_invoice_information",{
        property:window.property_name,
        posting_date:moment(tax_invoice_date.value).format("YYYY-MM-DD")
    }).then(result => {
        
        data.value = result.message
        isSaving.value = false
    })
    .catch(err=>{
        isSaving.value = false
    })
}


 

onMounted(() => {
    
    get_tax_invoice_info()
});


</script>