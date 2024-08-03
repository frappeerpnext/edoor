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
 <Calendar  @date-select="onDateSelect"  class="p-inputtext-sm w-full"
                                    v-model="tax_invoice_date" :placeholder="$t('Tax Invoice Date')"
                                    dateFormat="dd-mm-yy" showIcon showButtonBar panelClass="no-btn-clear"
                                     />
            </div>
            <div class="col-12">
                <!-- <table class="w-full">
                    <ComStayInfoNoBox label="Current Tax Invoice" :value="data?.current_counter" />
                    <ComStayInfoNoBox label="Next Tax Invoice" :value="data?.next_tax_invoice_number" /> 
                </table> -->
                <div class="col-12">
                    <label>{{$t('Tax Invoice Type')}}</label>
                    <ComSelect class="w-full min-w-full" id="dis_type" 
                     v-model="data.tax_invoice_type"  :options="['Tax Invoice','Commercial Invoice']" :clear="false" />
                </div>
                <div class="text-center shadow-1 p-3 mt-3 border-round-xl relative overflow-hidden">
                    <div v-tippy="'Update Exchange'" @click="opshow" class="bgsummaryday flex justify-content-center align-items-center conten-btn border-1 w-2rem h-2rem cursor-pointer  absolute right-2 top-1 border-circle border-round-xl">
<i class="pi pi-pencil" style="font-size: 12px;" />
                    </div>
                        <div class="text-2xl">Rate Exchange</div>
                        <span class="text-2xl">
                            <CurrencyFormat currAddClass="font-semibold" :value="1"  />({{ data?.base_currency }}) =
                            <CurrencyFormat currAddClass="font-semibold" :value="data.exchange_rate" :currency="data?.second_currency" /> ({{
                                data?.second_currency?.currency }})
                        </span>
                    </div>
            </div>
            <div class="col-12 flex justify-content-end">
           <!-- <Button class="conten-btn" @click="viewfoliotaxinvoicedetail()" label="Preview Before Generating" icon="pi pi-eye" />      -->
        </div>
        </div>
        
         
        <div class="relative mt-2">
            <span class="absolute w-full"><Checkbox class="w-full" v-model="isConfirm" :binary="true" /></span>
            <span class="pl-5">I am verify that all information is correct</span>
        </div>

        <OverlayPanel ref="op">
            <ComOverlayPanelContent :title="$t('Rate Exchange')" @onSave="onSaveEdit" :hideButtonClose="false" @onCancel="opshow(false)">
            <div class="grid my-2">
                <div class="col-4 flex align-items-center justify-content-center">
                    <CurrencyFormat currAddClass="font-semibold" :value="1" />({{ data?.base_currency }})  <span class="ms-3">=</span>     
                </div>
                <div class="col-8">
                    <div class="flex align-items-center">
<InputNumber inputClass="w-full" class="w-full" v-model="newExchange" :max="9999999999"  />
                   <span class="ms-2">({{ data?.second_currency?.currency }})</span> 
                    </div>
                    
                </div>
            </div>
            </ComOverlayPanelContent> 
        </OverlayPanel>

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
const data = ref({tax_invoice_type:""})
const confirm = useConfirm()
const gv = inject("$gv")
const op = ref();
const newExchange  = ref()
const opshow = (event) => { 
    newExchange.value  = data.value.exchange_rate   
  if (event == false) {
    op.value.hide() 
  }
  else {
      op.value.toggle(event);
  }
}
function onSaveEdit(){
    data.value.exchange_rate = newExchange.value
    op.value.hide() 
}
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
        document_type:dialogRef.value.data.document_type || "Reservation Folio",
        property:dialogRef.value.data.property,
        folio_number:dialogRef.value.data.name,
        tax_invoice_date:moment(tax_invoice_date.value).format("YYYY-MM-DD"),
        tax_invoice_type:data.value.tax_invoice_type || "",
        exchange_rate:data.value.exchange_rate
    }).then(result=>{
        isSaving.value = false
        dialogRef.value.close(result)
    }).catch(err=>{
        isSaving.value = false
    })
            },

        });
    
}
function viewfoliotaxinvoicedetail() {
     
     dialog.open(ComIFrameModal, {
         data: {
             doctype: "Tax Invoice",
             extra_params:[
				{key:'date',value: moment(tax_invoice_date.value).format("YYYY-MM-DD")},
			],
             name: dialogRef.value.data.name,
             report_name: gv.getCustomPrintFormat("Invoice"),
             letterhead:"Tax Letterhead",
             filter_options:["show_vattin","show_rate_type","show_business_source"]
            
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
        posting_date:moment(tax_invoice_date.value).format("YYYY-MM-DD"),
       
    }).then(result => {
        
        data.value = result.message
        isSaving.value = false
        newExchange.value = result.message.exchange_rate
    })
    .catch(err=>{
        isSaving.value = false
    })
}

function onDateSelect(event) {
    get_tax_invoice_info()
}
 

onMounted(() => {
    
    get_tax_invoice_info()

});


</script>