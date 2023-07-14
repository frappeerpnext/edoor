<template>
  <ComDialogContent :loading="loading" :hideButtonOK="true" @onClose="onClose">
    <div class="border-round-xl h-full">
        <div class="grid">
          <div class="col-6">
            <h2 data-v-c02f7a3a="" class="h-title mb-2">Transaction Detail</h2>
            <table class="">
              <tbody>
                <ComStayInfoNoBox label="Type" v-if="doc?.type" :value="doc?.type"/>
                <ComStayInfoNoBox label="Credit Card Number" v-if="doc?.credit_card_number" :value="doc?.credit_card_number" />
                <ComStayInfoNoBox label="Account Code" v-if="doc?.account_code" :value="doc?.account_code"/>
                <ComStayInfoNoBox label="Account Name" v-if="doc?.account_name" :value="doc?.account_name" />
                <ComStayInfoNoBox label="City Ledger Account" v-if="doc?.city_ledger_name && doc?.account_name == 'City Ledger Transfer'" :value="doc?.city_ledger_name" />
                <ComStayInfoNoBox label="Qty" v-if="doc?.account_name == 'Loundry'" :value="doc?.quantity" />
                <ComStayInfoNoBox label="Post Amount" v-if="doc?.input_amount" :value="doc?.input_amount" isCurrency />
                <ComStayInfoNoBox label="Amount/Rate" v-if="doc?.amount" :value="doc?.amount" isCurrency />
                <ComStayInfoNoBox label="Bank Name" v-if="doc?.bank_name" :value="doc?.bank_name" />
                <ComStayInfoNoBox label="Card Holder Name" v-if="doc?.card_holder_name" :value="doc?.card_holder_name" />
                <ComStayInfoNoBox label="Credit Expired Date" v-if="doc?.credit_expired_date" :value="gv.datetimeFormat(doc?.credit_expired_date)" />
                <ComStayInfoNoBox label="Bank Fee" v-if="doc?.bank_fee" :value="doc?.bank_fee" />
                <ComStayInfoNoBox label="Bank Fee Amount" v-if="doc?.bank_fee_amount" :value="doc?.bank_fee_amount" />
                <ComStayInfoNoBox label="Rate Before Tax" v-if="doc?.taxable_amount_1" :value="doc?.taxable_amount_1" isCurrency />
                <ComStayInfoNoBox label="Total Tax" v-if="doc?.total_tax" :value="doc?.total_tax" isCurrency isSlot>
                  <Button v-if="doc?.rate_include_tax != 'No'" @click="toggleTAX" icon="pi pi-question text-xs"
                    class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary" rounded outlined
                    aria-label="Total Tax" />
                  <OverlayPanel ref="opTax">
                    <div class="table-order-tax">
                      <table>
                        <tr>
                          <td class='p-2'>{{ doc?.tax_1_description }} : </td>
                          <td class='p-2 text-end'>
                            <CurrencyFormat :value="doc?.tax_1_amount" />
                          </td>
                        </tr>
                        <tr class='border-top-1' v-if="doc?.account_name == 'Minibar' || doc?.account_name != 'Loundry'">
                          <td class='p-2'>Spacial Tax-2% : </td>
                          <td class='p-2 text-end'>
                            <CurrencyFormat :value="doc?.tax_2_amount" />
                          </td>
                        </tr>
                        <tr class='border-top-1' v-else-if="doc?.account_name != 'Loundry'">
                          <td class='p-2'>{{ doc?.tax_2_description }} : </td>
                          <td class='p-2 text-end'>
                            <CurrencyFormat :value="doc?.tax_2_amount" />
                          </td>
                        </tr>
                        <tr class='border-top-1' v-if="doc?.account_name != 'Loundry'">
                          <td class='p-2'>{{ doc?.tax_3_description }} : </td>
                          <td class='p-2 text-end'>
                            <CurrencyFormat :value="doc?.tax_3_amount" />
                          </td>
                        </tr>
                      </table>
                    </div>
                  </OverlayPanel>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Discount Type" v-if="doc?.account_name == 'Room Charge' && doc?.discount" :value="doc?.discount_type" />
                <ComStayInfoNoBox label="Total Discount" v-if="doc?.discount_amount" :value="doc?.discount_amount" isCurrency />
                <ComStayInfoNoBox label="Total Amount" v-if="doc?.total_amount" :value="doc?.total_amount" isCurrency isSlot>
                  <Button v-if="doc?.amount && doc?.total_tax && doc?.discount" @click="togglePostAmount" icon="pi pi-question text-xs"
                    class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary" rounded outlined
                    aria-label="Total Tax" />
                    <OverlayPanel ref="opPostAmount">
                      <div class="table-order-tax">
                        <table>
                          <tr v-if="doc?.amount">
                            <td class='p-2'>Amount/Rate : </td>
                            <td class='p-2 text-end'>
                              <CurrencyFormat :value="doc?.amount" />
                            </td>
                          </tr>
                          <tr class='border-top-1' v-if="doc?.total_tax">
                            <td class='p-2'>Tax : </td>
                            <td class='p-2 text-end'>
                              <CurrencyFormat :value="doc?.total_tax" />
                            </td>
                          </tr>
                          <tr class='border-top-1' v-if="doc?.discount"> 
                            <td class='p-2'>- Discount : </td>
                            <td class='p-2 text-end'>
                              <CurrencyFormat :value="doc?.discount ? doc?.discount : '0'" />
                            </td>
                          </tr>
                          <tr class="border-top-1 border-black-alpha-90" v-if="doc?.total_amount">
                            <td class='p-2'>Total Amount : </td>
                            <td class='p-2 text-end'><CurrencyFormat :value="doc?.total_amount" /></td>
                          </tr>
                        </table>
                      </div>
                    </OverlayPanel>
                </ComStayInfoNoBox>
              </tbody>
            </table>
          </div>
          <div class="col-6">
            <h2 data-v-c02f7a3a="" class="h-title mb-2">Creation</h2>
            <table class="">
              <tbody>
                <ComStayInfoNoBox label="Folio" :value="doc?.name"/>
                <ComStayInfoNoBox label="Ref. No" v-if="setting.folio_transaction_stype_credit_debit == 1" isSlot :fill="false">
                  <Button class="p-0 link_line_action1" @click="changeRef($event)" link>
                    <span v-if="doc?.reference_number">{{doc?.reference_number}}</span>
                    <span v-else>Add Ref. No</span>
                  </Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox v-else-if="doc?.reference_number" label="Ref. No" :value="doc?.reference_number"/>
                <ComStayInfoNoBox label="Posted Date" :value="gv.datetimeFormat(doc?.posting_date)"/>
                <ComStayInfoNoBox label="Created Date" :value="gv.datetimeFormat(doc?.creation)"/>
                <ComStayInfoNoBox label="Made By" :value="doc?.owner"/>
                <ComStayInfoNoBox label="Last Modified by" :value="doc?.modified_by"/>
                <ComStayInfoNoBox label="Last Modified Date" :value="gv.datetimeFormat(doc?.modified)"/>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <hr class="my-2">
      <ComDocument doctype="Folio Transaction" :docname="doc?.name" v-if="!loading" :fill="false"/>

      <div v-if="doc.note" class="link_line_action_res_note px-3 mt-3">
        <div class="pt-2 pb-3 text-color-black" >
            <div class="">
                <div class="flex justify-content-between flex-wrap">
                    <span class="text-lg font-semibold line-height-4">Note</span>
                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onOpenNote"></Button>
                </div>
                <div class="text-sm">
                    <span class="font-italic">Last Modified: </span><span class="text-500 font-italic">{{doc?.note_by}} {{gv.datetimeFormat(doc?.note_modified)}}</span>
                </div>
            </div>
            <hr class="my-2">
            <div class="text-color wrap__sp_not">{{ doc?.note }}</div>
        </div>
      </div>
      <div v-else class="link_line_action px-3" @click="onOpenNote">
        <div  class="flex justify-center items-center my-3">
            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
            <span class="text-xl">Add Note</span>
        </div>
      </div>
      <div class="mt-3"> 
        <ComCommentAndNotice v-if="doc && doc?.name" doctype="Folio Transaction" :docname="doc?.name" :reservation="doc.reservation" :reservationStay="reservation_stay"/>
      </div>

    <template #footer-left v-if="setting.folio_transaction_stype_credit_debit != 1">
      <ComReservationStayFolioDetailActionMoreOptionsButton @onAuditTrail="onAuditTrail"/>
    </template>
    <OverlayPanel ref="openNote">
      <ComOverlayPanelContent width="350px" :loading="saving" @onSave="onSaveNote" @onCancel="onCloseNote">
          <div>
              <div>
                  <label for="textnote" class="text-lg font-semibold line-height-4">Note</label><br />
                  <Textarea class="w-full my-2" id="textnote" v-model="note" rows="5" />
              </div>
          </div>
      </ComOverlayPanelContent>
    </OverlayPanel>
  </ComDialogContent>

  <OverlayPanel ref="op">
    <ComOverlayPanelContent title="Change Ref. No" :loading="saving" @onSave="onSaveReferenceNumber" @onCancel="onCloseRefNumber">
      <div class="flex gap-2 my-2">
        <InputText type="text" v-model="refNum" />
      </div>
    </ComOverlayPanelContent>
  </OverlayPanel>
</template>
<script setup>
import { ref, getApi, inject, onMounted, updateDoc,useDialog,getDoc } from "@/plugin"
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioDetailActionMoreOptionsButton from '@/views/reservation/components/ComReservationStayFolioDetailActionMoreOptionsButton.vue';
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';

const props = defineProps({
  doctype: String
})

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const emit = defineEmits(['onClose'])
const dialogRef = inject("dialogRef")
const dialog = useDialog()
const gv = inject('$gv')
const doc = ref({})
const openNote = ref()
const op = ref()
const note = ref('')
const loading = ref(false)
const saving = ref(false)
const refNum = ref()
const onClose = () =>{
  dialogRef.value.close();
}

const changeRef = ($event) => {
    refNum.value = doc.value.reference_number
    op.value.toggle($event);
}
function onCloseRefNumber(){
  op.value.hide()
}
const onSaveReferenceNumber = () => {
  saving.value = true
  const data = JSON.parse(JSON.stringify(doc.value))
  data.reference_number = refNum.value
  updateDoc('Folio Transaction', doc.value.name, data).then((r)=>{
    saving.value = false
    doc.value = r
    onCloseRefNumber()
  }).catch(()=>{
    saving.value = false
  })
}

const opTax = ref();
const opPostAmount = ref();
const toggleTAX = (event) => {
  opTax.value.toggle(event);
}

const togglePostAmount = (event) => {
  opPostAmount.value.toggle(event);
}


const onOpenNote = ($event) =>{
  const data = JSON.parse(JSON.stringify(doc.value))
  note.value = data.note
  openNote.value.toggle($event)
}
const onCloseNote = ($event) =>{
  openNote.value.hide()
}
function onSaveNote(){
  saving.value = true
  const data = JSON.parse(JSON.stringify(doc.value))
  data.note = note.value
  updateDoc('Folio Transaction', doc.value.name,data).then((r)=>{
    saving.value = false
    doc.value = r
    onCloseNote()
  }).catch(()=>{
    saving.value = false
  })
}
function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Folio Transaction',
            docname: doc.value.name
        },
        props: {
            header: 'Audit Trail',
            style: {
                width: '75vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {
            //
        }
    });
}
onMounted(() => {

  if (dialogRef.value.data.folio_transaction_number) {

    loading.value = true
    // getApi("reservation.get_folio_transaction",{
    //   folio_number: dialogRef.value.data.folio_transaction_number
    // })
    //   .then((result) => {
    //     console.log(result)
    //    doc.value = result.message.folio_transaction
    //    accountCode.value = result.message.account_code
    //     loading.value = false
    //   }).catch((err) => {
    //     loading.value = false
    //   })
    
      getDoc("Folio Transaction", dialogRef.value.data.folio_transaction_number).then((r)=>{
        doc.value = r
        loading.value = false
      }).catch(()=>{
        loading.value = false
      })
  }
})

</script>
<style scoped>
.link_line_action_res_note {
  border: 1px dashed #d1d4e5;
  border-radius: 10px;
  padding: 0 5px;
  display: inline-block;
  width: 100%;
  background-color: #fdfdff;
}
table {
  border-collapse: collapse;
  border: 1px solid rgba(204, 204, 204, 0.3);
  width: 100%;
}
th, td {
  padding: .5rem;
  text-align: left;
  border-bottom: 1px solid rgba(204, 204, 204, 0.3);
}
th {
  border-top: 1px solid rgba(204, 204, 204, 0.3);
  border-bottom: 2px solid rgba(204, 204, 204, 0.3);
  border-left: 1px solid rgba(204, 204, 204, 0.3);
  font-weight: normal;
}
td{
  border-top: 1px solid rgba(204, 204, 204, 0.3);
  border-bottom: 1px solid rgba(204, 204, 204, 0.3);
  border-left: 1px solid rgba(204, 204, 204, 0.3);
  vertical-align: baseline;
}
tr:last-of-type td {
  border-bottom: none;
}
</style>