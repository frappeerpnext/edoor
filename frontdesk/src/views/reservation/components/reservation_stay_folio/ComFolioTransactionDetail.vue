<template>
  <ComDialogContent :loading="loading" :hideButtonOK="true" @onClose="onClose">
    <div class="border-round-xl h-full">
      <div class="grid">
        <div class="col-12 md:col-6">
          <h2 data-v-c02f7a3a="" class="font-semibold h-title mb-2">
          {{ $t('Transaction Detail') }}
            </h2>
          <table class="">
            <tbody>
              <ComStayInfoNoBox label="Room Number" v-if="doc?.room_number" :value="doc.room_number" />
              <ComStayInfoNoBox v-tippy="doc.guest_name.length > 20 ? doc.guest_name : ''" label="Guest" class="w-full"
                v-if="doc?.guest_name">
                <span @click="onViewCustomerDetail(doc.guest)"
                  class="-ml-2 overflow-hidden white-space-nowrap text-right link_line_action1 text-overflow-ellipsis">
                  {{ doc.guest }} - {{ doc.guest_name }}
                </span>
              </ComStayInfoNoBox>

              <ComStayInfoNoBox label="Sale Number" class="w-full" v-if="doc?.sale">
                <span @click="onViewSaleDetail()"
                  class="-ml-2 overflow-hidden white-space-nowrap text-right link_line_action1 text-overflow-ellipsis">
                  {{ doc.sale }}
                </span>
              </ComStayInfoNoBox>

              <ComStayInfoNoBox label="Folio Number" v-if="doc?.transaction_number" :value="doc.transaction_number" />
              <ComStayInfoNoBox label="Type" v-if="doc?.type" :value="doc?.type" />
              <ComStayInfoNoBox label="Bank Name" v-if="doc?.bank_name" :value="doc?.bank_name" />
              <ComStayInfoNoBox label="Credit Card Number" v-if="doc?.credit_card_number"
                :value="doc?.credit_card_number" />
              <ComStayInfoNoBox label="Account Code" v-if="doc?.account_code" :value="doc?.account_code" />
              <ComStayInfoNoBox label="Account Name" v-if="doc?.account_name" :value="doc?.account_name" />
              <ComStayInfoNoBox label="Payment By" v-if="doc?.payment_by" :value="doc?.payment_by" />
              <ComStayInfoNoBox label="Phone Number" v-if="doc?.payment_by_phone_number"
                :value="doc?.payment_by_phone_number" />


              <ComStayInfoNoBox :label="doc.target_transaction_type" isSlot :fill="false"
                v-if="doc.target_transaction_type">

                <Button class="p-0 link_line_action1" @click="onOpenLink()" link>
                  <span>{{ doc?.target_transaction_number }}</span>

                </Button>
              </ComStayInfoNoBox>
              <ComStayInfoNoBox label="Post Amount" v-if="doc?.input_amount" :value="doc?.input_amount" isCurrency />
              <ComStayInfoNoBox label="Qty"
                v-if="account_code?.allow_enter_quantity == 1 || doc?.allow_enter_quantity == 1 && doc?.account_code"
                :value="doc?.quantity" />
              <ComStayInfoNoBox label="Amount/Rate" v-if="doc?.amount" :value="doc?.amount" isCurrency />
              <ComStayInfoNoBox label="Card Holder Name" v-if="doc?.card_holder_name" :value="doc?.card_holder_name" />
              <ComStayInfoNoBox label="Credit Expired Date" v-if="doc?.credit_expired_date"
                :value="gv.datetimeFormat(doc?.credit_expired_date)" />
              <ComStayInfoNoBox label="Bank Fee" v-if="doc?.bank_fee" :value="doc?.bank_fee + ' %'" />
              <ComStayInfoNoBox label="Bank Fee Amount" v-if="doc?.bank_fee_amount"
                :value="'$ ' + doc?.bank_fee_amount" />
              <ComStayInfoNoBox label="Rate Include Tax" v-if="doc?.rate_include_tax != 'No' && account_code.allow_tax"
                :value="doc?.rate_include_tax" />
              <ComStayInfoNoBox label="Rate Include Tax" v-if="doc?.rate_include_tax != 'Yes' && account_code.allow_tax"
                :value="doc?.rate_include_tax" />
              <ComStayInfoNoBox label="Rate Before Tax"
                v-if="doc?.tax_rule_data && (doc?.tax_rule_data?.tax_1_rate + doc?.tax_rule_data?.tax_2_rate + doc?.tax_rule_data?.tax_3_rate > 0) && doc?.account_code"
                :value="doc?.amount" isCurrency />
              <ComStayInfoNoBox label="Total Tax" v-if="account_code?.allow_tax && doc?.account_code"
                :value="doc?.total_tax" isCurrency isSlot>
                <Button @click="toggleTAX" icon="pi pi-question text-xs"
                  class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary" rounded outlined
                  aria-label="Total Tax" />
                <OverlayPanel ref="opTax">
                  <div class="table-order-tax">
                    <table class="inner-tip-tab">
                      <tr v-if="doc?.tax_rule_data && doc?.tax_rule_data?.tax_1_rate > 0">
                        <td class='p-2'>{{ doc?.tax_rule_data?.tax_1_name || '' }} - {{ doc?.tax_rule_data?.tax_1_rate ||
                          0 }}% : </td>
                        <td class='p-2 text-end'>
                          <CurrencyFormat :value="doc?.tax_1_amount" />
                        </td>
                      </tr>
                      <tr class='border-top-1' v-if="doc?.tax_rule_data && doc?.tax_rule_data?.tax_2_rate > 0">
                        <td class='p-2'>{{ doc?.tax_rule_data?.tax_2_name || '' }} - {{ doc?.tax_rule_data?.tax_2_rate ||
                          0 }}% :</td>
                        <td class='p-2 text-end'>
                          <CurrencyFormat :value="doc?.tax_2_amount" />
                        </td>
                      </tr>
                      <tr class='border-top-1' v-if="doc?.tax_rule_data && doc?.tax_rule_data?.tax_3_rate > 0">
                        <td class='p-2'>{{ doc?.tax_rule_data?.tax_3_name || '' }} - {{ doc?.tax_rule_data?.tax_3_rate ||
                          0 }}% :</td>
                        <td class='p-2 text-end'>
                          <CurrencyFormat :value="doc?.tax_3_amount" />
                        </td>
                      </tr>
                    </table>
                  </div>
                </OverlayPanel>
              </ComStayInfoNoBox>

              <ComStayInfoNoBox label="Discount Amount" v-if="doc?.discount > 0 && doc?.account_code"
                :value="doc?.discount_amount" isCurrency>
                <Button v-if="doc?.discount" @click="togglePostDiscountAmount" icon="pi pi-question text-xs"
                  class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary" rounded outlined
                  aria-label="Total Tax" />
                <OverlayPanel ref="opPostDiscountAmount">
                  <div class="table-order-tax">
                    <table class="inner-tip-tab">
                      <tr>
                        <td class='p-2'>Discount Type : </td>
                        <td class='p-2 text-end'>
                          {{ doc?.discount_type + ' ' + (doc?.discount_type == 'Percent' ? doc?.discount + '%' : '') }}
                        </td>
                      </tr>
                    </table>
                  </div>
                </OverlayPanel>
              </ComStayInfoNoBox>

              <ComStayInfoNoBox label="Total Amount" v-if="doc?.total_amount" :value="doc?.total_amount" isCurrency
                isSlot>
                <Button v-if="doc?.amount || doc?.total_tax || doc?.discount" @click="togglePostAmount"
                  icon="pi pi-question text-xs" class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary"
                  rounded outlined aria-label="Total Tax" />
                <OverlayPanel ref="opPostAmount">
                  <div class="table-order-tax">
                    <table class="inner-tip-tab">
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
                      <tr class='border-top-1' v-if="doc?.discount > 0 && doc?.account_code">
                        <td class='p-2'>Discount : </td>
                        <td class='p-2 text-end'>
                          -
                          <CurrencyFormat :value="doc?.discount_amount ? doc?.discount_amount : '0'" />
                        </td>
                      </tr>
                      <tr class="border-top-1 border-black-alpha-90" v-if="doc?.total_amount">
                        <td class='p-2'>Total Amount : </td>
                        <td class='p-2 text-end'>
                          <CurrencyFormat :value="doc?.total_amount" />
                        </td>
                      </tr>
                    </table>
                  </div>
                </OverlayPanel>
              </ComStayInfoNoBox>
              <ComStayInfoNoBox v-if="doc?.account_name == 'Folio Transfer'" :fill="false"
                :label="doc?.account_name == 'Folio Transfer' && doc?.type == 'Credit' ? 'Folio Transfer to' : 'Folio transferred from'"
                isSlot>
                <Button class="p-0 link_line_action1" @click="onOpenFolioDetail(doc.folio_number)" link>{{
                  doc.folio_number }}</Button>
              </ComStayInfoNoBox>
            </tbody>
          </table>
        </div>
        <div class="col-12 md:col-6">
          <h2 data-v-c02f7a3a="" class="font-semibold h-title mb-2">
            {{ $t('Creation') }}
            </h2>
          <table class="">
            <tbody>
              <ComStayInfoNoBox label="Folio Transaction No" :value="doc?.name" />
              <ComStayInfoNoBox label="Ref. No" isSlot :fill="false">
                <Button class="p-0 link_line_action1" @click="changeRef($event)" link>
                  <span v-if="doc?.reference_number">{{ doc?.reference_number }}</span>
                  <span v-else>Add Ref. No</span>
                </Button>

              </ComStayInfoNoBox>
              <!-- <ComStayInfoNoBox v-else label="Ref. No" :value="doc?.reference_number"/> -->
              <ComStayInfoNoBox label="Posted Date" :value="moment(doc?.posting_date).format('DD-MM-YYYY')" />
              <ComStayInfoNoBox label="Create By" :value="doc?.owner?.split('@')[0]" />
              <ComStayInfoNoBox label="Created Date" isSlot :fill="false">
                <div class="font-semibold">
                  <ComTimeago :date="doc?.creation" />
                </div>
              </ComStayInfoNoBox>
              <ComStayInfoNoBox label="Last Modified by" :value="doc?.modified_by?.split('@')[0]" />
              <ComStayInfoNoBox label="Last Modified Date" isSlot :fill="false">
                <div class="font-semibold">
                  <ComTimeago :date="doc?.modified" />
                </div>
              </ComStayInfoNoBox>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <hr class="my-2">
    <ComDocument doctype="Folio Transaction" :docname="doc?.name" v-if="!loading" :fill="true" :attacheds="[doc?.name]" />

    <div v-if="doc.note" class="link_line_action_res_note px-3 mt-3">
      <div class="pt-2 pb-3 text-color-black">
        <div class="">
          <div class="flex justify-content-between flex-wrap">
            <span class="text-lg font-semibold line-height-4">Note</span>
            <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onOpenNote"></Button>
          </div>
          <div class="text-sm">
            <span class="font-italic">Last Modified: </span><span class="text-500 font-italic">{{ doc?.note_by }}
              {{ gv.datetimeFormat(doc?.note_modified) }}</span>
          </div>
        </div>
        <hr class="my-2">
        <div class="text-color wrap__sp_not">{{ doc?.note }}</div>
      </div>
    </div>
    <div v-else class="link_line_action px-3 mt-3" @click="onOpenNote">
      <div class="flex justify-center items-center my-3">
        <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
        <span class="text-xl">Add Note</span>
      </div>
    </div>
    <div class="mt-3">
      <ComCommentAndNotice v-if="doc && doc?.name" doctype="Folio Transaction" :docname="doc?.name"
        :filters="['custom_folio_transaction', '=', doc.name]" />
    </div>

    <template #footer-left>


      <Button class="border-none" @click="onPrintFolioTransaction" :label="$t('Print')" icon="pi pi-print"
        v-if="doc.print_format" />
      <Button class="border-none" @click="onAuditTrail" :label="$t('Audit Trail')" icon="pi pi-history" />
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
    <ComOverlayPanelContent title="Change Ref. No" :loading="saving" @onSave="onSaveReferenceNumber"
      @onCancel="onCloseRefNumber">
      <div class="flex gap-2 my-2">
        <InputText type="text" v-model="refNum" />
      </div>
    </ComOverlayPanelContent>
  </OverlayPanel>
</template>
<script setup>
import { ref, getApi, inject, onMounted, updateDoc, useDialog, postApi, onUnmounted } from "@/plugin"
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioDetailActionMoreOptionsButton from '@/views/reservation/components/ComReservationStayFolioDetailActionMoreOptionsButton.vue';
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import ComCommentAndNotice from '@/components/form/ComCommentAndNotice.vue';
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
  doctype: String
})

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const emit = defineEmits(['onClose'])
const dialogRef = inject("dialogRef")
const moment = inject("$moment")
const dialog = useDialog()
const gv = inject('$gv')
const doc = ref({})
const account_code = ref({})
const openNote = ref()
const op = ref()
const note = ref('')
const loading = ref(false)
const saving = ref(false)
const refNum = ref()
const onClose = () => {
  dialogRef.value.close();
}


const changeRef = ($event) => {
  if (!gv.cashier_shift?.name) {
    gv.toast('error', 'Please Open Cashier Shift.')
    return
  }
  refNum.value = doc.value.reference_number
  op.value.toggle($event)
}

function onCloseRefNumber() {
  op.value.hide()
}

const onSaveReferenceNumber = () => {
  saving.value = true
  const data = JSON.parse(JSON.stringify(doc.value))
  data.reference_number = refNum.value
  postApi('utils.update_doctype_data', {
    data: {
      doctype: "Folio Transaction",
      name: data.name,
      reference_number: data.reference_number || ""
    }
  }).then((r) => {

    doc.value.reference_number = r.message.reference_number
    saving.value = false
    onLoad(false)
    window.postMessage({action:"FolioTransactionList"},"*")
    window.postMessage({action:"ReservationStayDetail"},"*") 

    onCloseRefNumber()
  }).catch(() => {
    saving.value = false
  })
}

const opTax = ref();
const opPostAmount = ref();
const opPostDiscountAmount = ref();
const toggleTAX = (event) => {
  opTax.value.toggle(event);
}

const togglePostAmount = (event) => {
  opPostAmount.value.toggle(event);
}
const togglePostDiscountAmount = (event) => {
  opPostDiscountAmount.value.toggle(event);
}
const onOpenNote = ($event) => {
  if (!gv.cashier_shift?.name) {
    gv.toast('error', 'Please Open Cashier Shift.')
    return
  }
  const data = JSON.parse(JSON.stringify(doc.value))
  note.value = data.note
  openNote.value.toggle($event)
}
const onCloseNote = ($event) => {
  openNote.value.hide()
}

function onSaveNote() {
  saving.value = true

  postApi('utils.update_doctype_data', {
    data: {
      "doctype": "Folio Transaction",
      name: doc.value.name,
      note: note.value
    }
  }).then((r) => {
    onCloseNote()
    saving.value = false
    doc.value.note = r.message.note
    doc.value.modified = r.message, modified
    doc.value.modified_by = r.message.modified_by

  }).catch(() => {
    saving.value = false
  })
}
function onAuditTrail() {
  const dialogRef = dialog.open(ComAuditTrail, {
    data: {
      doctype: 'Folio Transaction',
      docname: doc?.value.name,
      referenceTypes: [
        { doctype: 'Folio Transaction', label: 'Folio Transaction' },
      ],
      filter_key: "custom_folio_transaction"
    },
    props: {
      header: $t('Audit Trail for Folio Transaction'),
      style: {
        width: '80vw',
      },
      modal: true,
      maximizable: true,
      closeOnEscape: false,
      position: "top",
      breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
    },
    onClose: (options) => {
      //
    }
  });
}

function onOpenFolioDetail(name) {
  window.parent.postMessage('view_folio_detail|' + name, '*')
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="FolioTransactionDetail"){
            setTimeout(()=>{
              onLoad(false)
            },1000*2)
            
        }
    };
}

onMounted(() => {
  if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
  window.folio_transaction_number = dialogRef.value.data.folio_transaction_number
  window.addEventListener('message', actionRefreshData, false);
  onLoad()
})
function onLoad(showLoading = true) {
  if (dialogRef.value.data.folio_transaction_number) {
    loading.value = showLoading
    getApi("reservation.get_folio_transaction_detail", {
      name: dialogRef.value.data.folio_transaction_number
    })
      .then((result) => {
        doc.value = result.message.folio_transaction
        doc.value.tax_rule_data = JSON.parse(result.message.folio_transaction.tax_rule_data)
        account_code.value = result.message.account_code
        loading.value = false
      }).catch((err) => {
        loading.value = false
      })
  }
}
function onPrintFolioTransaction() {
  const dialogRef = dialog.open(ComIFrameModal, {
    data: {
      doctype: "Folio Transaction",
      name: doc.value.name,
      report_name: doc.value.print_format,
    },
    props: {
      header: 'Print Preview',
      style: {
        width: '80vw',
      },
      position: "top",
      modal: true,
      breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
    },
  })
}

function onViewCustomerDetail(name) {
  if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
  window.postMessage('view_guest_detail|' + name, '*')
}
function onViewSaleDetail() {
  const dialogRef = dialog.open(ComIFrameModal, {
    data: {
      doctype: "Sale",
      name: doc.value.sale,
      report_name: "Sale Receipt",
    },
    props: {
      header: 'Print Preview',
      style: {
        width: '80vw',
      },
      position: "top",
      modal: true,
      breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
    },
  })
}
function onOpenLink() {
  window.postMessage("view_" + doc.value.target_transaction_type.toLowerCase().replaceAll(" ", "_") + "_detail|" + doc.value.target_transaction_number)
}


onUnmounted(() => {
  window.removeEventListener('message', actionRefreshData, false);
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

table:not(.inner-tip-tab) {
  border-collapse: collapse;
  border: 1px solid rgba(204, 204, 204, 0.3);
  width: 100%;
}

table:not(.inner-tip-tab) th,
table:not(.inner-tip-tab) td {
  padding: .5rem;
  text-align: left;
  border-bottom: 1px solid rgba(204, 204, 204, 0.3);
}

table:not(.inner-tip-tab) th {
  border-top: 1px solid rgba(204, 204, 204, 0.3);
  border-bottom: 2px solid rgba(204, 204, 204, 0.3);
  border-left: 1px solid rgba(204, 204, 204, 0.3);
  font-weight: normal;
}

table:not(.inner-tip-tab) td {
  border-top: 1px solid rgba(204, 204, 204, 0.3);
  border-bottom: 1px solid rgba(204, 204, 204, 0.3);
  border-left: 1px solid rgba(204, 204, 204, 0.3);
  vertical-align: baseline;
}

table:not(.inner-tip-tab) tr:last-of-type td {
  border-bottom: none;
}</style>