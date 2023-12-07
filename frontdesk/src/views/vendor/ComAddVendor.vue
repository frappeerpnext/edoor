<template>
  <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="grid">
      <div class="col-12">
        <ComReservationStayPanel title="Vendor Information">
          <template #content>
            <div class="grid">
              <div class="col-6">
                <label>Vendor Name</label>
                <InputText v-model="data.name" type="text" class="w-full" placeholder="Vendor Name" />
              </div>
              <div class="col-6">
                <label>Company</label>
                <InputText v-model="data.company" type="text" class="w-full" placeholder="Company" />
              </div>
              <div class="col-6">
                <label>Vendor Type</label>
                <ComAutoComplete class="w-full" v-model="data.vendor_type" placeholder="Vendor Type"
                  doctype="Customer Group" />
              </div>
              <div class="col-6">
                <label>Vendor Group</label>
                <ComAutoComplete class="w-full" v-model="data.vendor_group" placeholder="Vendor Group"
                  doctype="Vendor Group" />
                <div class="col-12">
                  <Checkbox inputId="ingredient1" v-model="data.auto_create_city_ledger_account" :binary="true" />
                  <label for="ingredient1" class="ml-2">Disabled</label>
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
                <label>Contact Name</label>
                <InputText v-model="data.contact_name" type="text" class="w-full" placeholder="Contact Name" />
              </div>
              <div class="col-6">
                <label>Email Address</label>
                <InputText v-model="data.email_address" type="text" class="w-full" placeholder="Email Address" />
              </div>
              <div class="col-6">
                <label>Phone Number</label>
                <InputText v-model="data.phone_number" type="text" class="w-full" placeholder="Phone Number" />
              </div>
              <div class="col-6">
                <label>Website</label>
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
                <label>Province</label>
                <InputText v-model="data.province" type="text" class="w-full" placeholder="Province" />
              </div>

              <div class="col-12 lg:col-6 pt-1">
                <label class="white-space-nowrap">Address</label><br />
                <Textarea class="p-inputtext-sm w-full" placeholder="Address" v-model="data.address" rows="4" />
              </div>
              <div class="col-12 lg:col-6 pt-1">
                <label class="white-space-nowrap">Note</label><br />
                <Textarea class="p-inputtext-sm w-full" placeholder="Note" v-model="data.note" rows="4" />
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
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
const data = ref({})
const loading = ref(false)


function onLoad() {
  loading.value = true
  getDoc('Business Source', dialogRef.value.data.name)
    .then((r) => {
      data.value = r
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
  if (!data.value.business_source) {
    gv.toast('warn', 'Bussiness source is required.')
    return
  }
  else if (!data.value.business_source_type) {
    gv.toast('warn', 'Bussiness source type is required.')
    return
  }
  loading.value = true
  const rename = {
    old_name: dialogRef.value.data.name,
    new_name: data.value.business_source
  }
  createUpdateDoc("Business Source", data.value, '', rename).then((r) => {

    window.socket.emit("Vendor", window.property_name)
    dialogRef.value.close(rename.new_name)
  }).catch((err) => {
    loading.value = false
  })
}

onMounted(() => {
  if (dialogRef.value.data.name) {
    onLoad()
  } else {
    data.value.property = window.property_name
  }
})
</script>