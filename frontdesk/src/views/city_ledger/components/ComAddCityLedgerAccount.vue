<template> 
    <ComDialogContent @onClose="onClose" @onOK="onSave">
        <ComReservationStayPanel title="City Ledger Information">
            <template #content>
                <div class="grid">
                <div class="col-6">
                    <label>City Ledger Name</label>
                    <InputText class="w-full" v-model="data.city_ledger_name" type="text" placeholder="City Ledger Name" :maxlength="50" />
                </div>
                <div class="col-6">
                    <label>City Ledger Type</label>
                    <ComSelect class="w-full" v-model="data.city_ledger_type" placeholder="City Ledger Type" doctype="City Ledger Type" />
                </div>
                <div class="col-6">
                    <label>Business Source</label>
                    <ComSelect class="w-full" v-model="data.business_source" placeholder="Business Source" doctype="Business Source" />
                </div>
                <div class="col-6">
                    <label>Company Name</label><br />
                    <InputText class="w-full" v-model="data.company_name" type="text"  placeholder="Company Name" :maxlength="50" />
                </div>
                </div>
            </template>
        </ComReservationStayPanel>
        <div class="col-6">
            <label>Phone Number</label><br />
            <InputText v-model="data.phone_number" type="number"  placeholder="Phone Number" :maxlength="50" />
        </div>
        <div>
            <label>Email Address</label><br />
            <InputText v-model="data.email_address" type="text"  placeholder="Email Address" :maxlength="50" />
        </div>
        <b>Contact Info</b>
        <div>
            <label>Contact Name</label><br />
            <InputText v-model="data.contact_name" type="text"  placeholder="Contact Name" :maxlength="50" />
        </div>
        <div>
            <label>Phone Number</label><br />
            <InputText v-model="data.contact_phone_number" type="number"  placeholder="Phone Number" :maxlength="50" />
        </div>
        <div>
            <label>Bank Account Number</label><br />
            <InputText v-model="data.bank_account_number" type="number"  placeholder="Bank Account Number" :maxlength="50" />
        </div>
        <div>
            <label>Bank Account Name</label><br />
            <InputText v-model="data.bank_account_name" type="text"  placeholder="Bank Account Name" :maxlength="50" />
        </div>
        <div>
            <label>Bank Name</label><br />
            <InputText v-model="data.bank_name" type="text"  placeholder="Bank Name" :maxlength="50" />
        </div>
        
        <div class="col-12">
            <label>Note</label>
            <div class="card flex justify-content-left">
                <Textarea v-model="data.note"  rows="3"  style="width: 100%;" />
            </div>
        </div>
        <div class="col-12">
            <label>Address</label>
            <div class="card flex justify-content-left">
                <Textarea v-model="data.address"  rows="3"  style="width: 100%;" />
            </div>
          </div>
       
    </ComDialogContent>
</template>
<script setup>
import { ref, createUpdateDoc,inject,getDoc,onMounted } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
const loading = ref(false);

const socket = inject("$socket")

const property = JSON.parse(localStorage.getItem( "edoor_property"))
const data = ref({property:property.name})
function onClose(){
    dialogRef.value.close()
}

function onSave(){
    
  loading.value = true
  createUpdateDoc("City Ledger", {data: data.value}).then((r)=>{
    loading.value = false
    dialogRef.value.close(r)
    socket.emit("RefreshData", {property:property.name,action:"refresh_city_ledger"});
  }).catch((err)=>{
    loading.value = false
  })
}
onMounted(() => {
  if(dialogRef.value.data.name){
    getDoc("City Ledger", dialogRef.value.data.name).then((r)=>{
      data.value = r
    })
  }
})
</script>