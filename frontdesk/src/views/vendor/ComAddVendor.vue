<template>
  <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="grid">
      <div class="col-12">
        <ComReservationStayPanel title="Vendor Information">
          <template #content>
            <div class="grid">
              <div class="col-6">
                <label> {{ $t('Vendor Name') }} </label>
                <InputText v-model="data.vendor_name" type="text" class="w-full" placeholder="Vendor Name" />
              </div>
              <div class="col-6">
                <label>{{ $t('Company') }} </label>
                <InputText v-model="data.company" type="text" class="w-full" placeholder="Company" />
              </div>
              <div class="col-6">
                <label> {{ $t('Vendor Type') }} </label>
                <ComSelect width="100%" v-model="data.vendor_type" @onSelected="onSearch"
                    placeholder="Vendor Type" :options="[ 'Individual','General','Company']" />
              </div>
              <div class="col-6">
                <label> {{ $t('Vendor Group') }} </label>
                <ComAutoComplete class="w-full" v-model="data.vendor_group" placeholder="Vendor Group"
                  doctype="Vendor Group" />
                <div class="col-12">
                  <Checkbox inputId="ingredient1" v-model="data.disabled" :binary="true" />
                  <label for="ingredient1" class="ml-2"> {{ $t('Disabled') }} </label>
                </div>
              </div>
            </div>
          </template>
        </ComReservationStayPanel>
      </div>
      <div class="col-12">
        <ComReservationStayPanel title="Contact Information">
          <template #content>
            <div class="grid">
              <div class="col-6">
                <label> {{ $t('Contact Name') }} </label>
                <InputText v-model="data.contact_name" type="text" class="w-full" placeholder="Contact Name" />
              </div>
              <div class="col-6">
                <label> {{ $t('Email Address') }} </label>
                <InputText v-model="data.email_address" type="text" class="w-full" placeholder="Email Address" />
              </div>
              <div class="col-6">
                <label> {{ $t('Phone Number') }} </label>
                <InputText v-model="data.phone_number" type="text" class="w-full" placeholder="Phone Number" />
              </div>
              <div class="col-6">
                <label> {{ $t('Website') }} </label>
                <InputText v-model="data.website" type="text" class="w-full" placeholder="Website" />
              </div>
            </div>
          </template>
        </ComReservationStayPanel>
      </div>
      <div class="col-12">
        <ComReservationStayPanel title="Address & Note">
          <template #content>
            <div class="grid">
              <div class="col-12">
                <label> {{ $t('Province') }} </label>
                <InputText v-model="data.province" type="text" class="w-full" placeholder="Province" />
              </div>

              <div class="col-12 lg:col-6 pt-1">
                <label class="white-space-nowrap"> {{ $t('Address') }} </label><br />
                <Textarea class="p-inputtext-sm w-full" :placeholder=" $t('Address')" v-model="data.address" rows="4" />
              </div>
              <div class="col-12 lg:col-6 pt-1">
                <label class="white-space-nowrap"> {{ $t('Note') }} </label><br />
                <Textarea class="p-inputtext-sm w-full" :placeholder=" $t('Note') " v-model="data.note" rows="4" />
              </div>

            </div>
          </template>
        </ComReservationStayPanel>
      </div>
    </div>
  </ComDialogContent>
</template>
<script setup>
import { ref, createUpdateDoc, inject, getDoc, onMounted } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
const data = ref({})
const loading = ref(false)


function onLoad() {
  loading.value = true
  getDoc('Vendor', dialogRef.value.data.name)
    .then((r) => {
      data.value = r
      window.postMessage({action:"Vendor"},"*")
      window.postMessage({action:"ComVendorDetail"},"*")
      window.postMessage({action:"PayableLedger"},"*")
      window.postMessage({action:"ComPayableLedgerDetail"},"*")
      loading.value = false
    })
    .catch((error) => {
      loading.value = false
    });
}

function onClose() {
  dialogRef.value.close()
}

function onSave() {
  if (!data.value.vendor_name) {
      gv.toast('warn', 'vendor name is required.')
      return
  }
  if (!data.value.vendor_type) {
      gv.toast('warn', 'vendor type is required.')
      return
  }

  loading.value = true
  createUpdateDoc("Vendor", data.value).then((r) => {
    onLoad()
    dialogRef.value.close()
  }).catch((err) => {
    loading.value = false
  })
}

onMounted(() => {
  if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
  if (dialogRef.value.data.name) {
    onLoad()
  }
  //  else {
  //   data.value.property = window.property_name
  // }
})
</script>