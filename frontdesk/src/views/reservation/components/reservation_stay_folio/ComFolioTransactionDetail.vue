<template>
  {{ doc }}
  <ComDialogContent :loading="isLoading" hideButtonClose>
    <div class="bg-card-info border-round-xl p-3 h-full">
      <div class="grid">
        <div class="col-6">
          <div class="flex gap-2">
            <ComBoxStayInformation titleClass="p-0 justify-content-end w-7rem" titleTooltip="Folio Name" title="Folio Name"
              :value="doc?.name" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-6">
          <div class="flex gap-2">
            <ComBoxStayInformation titleClass="p-0 justify-content-end w-7rem" titleTooltip="Posting Date" title="Posting Date"
              :value="doc?.posting_date" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-6">
          <div class="flex gap-2">
            <ComBoxStayInformation titleClass="p-0 justify-content-end w-7rem" titleTooltip="Acount" title="Acount"
              :value="doc?.account_name" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <!-- <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Quantity" title="Quantity"
              :value="doc?.quantity" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Amount" title="Amount"
              :value="doc?.amount" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Discount" title="Discount"
              :value="doc?.discount ? doc?.discount : '0'" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Tax" title="Tax"
              :value="doc?.tax" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Bank Fee" title="Bank Fee"
              :value="doc?.bank_fee ? doc?.bank_fee : '0'" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Total Amount" title="Total Amount"
              :value="doc?.total_amount" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Made By" title="Made By"
              :value="doc?.owner" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-4">
          <div class="">
            <ComBoxStayInformation titleClass="p-0 justify-content-end" titleTooltip="Created" title="Created"
              :value="doc?.creation" valueClass="grow"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col-12">
          <div class="">
              <Textarea placeholder="Note" class="w-full" v-model="doc.note" />
          </div>
        </div> -->
      </div>
    </div>
  </ComDialogContent>
</template>
<script setup>
import { ref, getDoc, inject, onMounted } from "@/plugin"
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
const dialogRef = inject("dialogRef");

const doc = ref({})
const isLoading = ref(false)


onMounted(() => {

  if (dialogRef.value.data.folio_transaction_number) {

    isLoading.value = true
    getDoc("Folio Transaction", dialogRef.value.data.folio_transaction_number)
      .then((result) => {
        doc.value = result
        isLoading.value = false
      }).catch((err) => {
        isLoading.value = false
      })
  }
})
</script>