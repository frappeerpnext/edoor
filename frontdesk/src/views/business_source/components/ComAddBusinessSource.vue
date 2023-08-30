<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
        <div class="grid">
            <div class="col-12">
                <ComReservationStayPanel title="Business Source Information">
                    <template #content>
                <div class="grid">
                <div class="col-6">
                    <label>Business Source Type</label>
                    <ComSelect v-model="data.business_source_type" class="w-full"  placeholder="Business Source Type" doctype="Business Source Type" />
                </div>
                <div class="col-6">
                    <label>Business Source</label> 
                    <InputText v-model="data.business_source" type="text" class="w-full"  placeholder="Business Source" />
                </div>
                <div class="col-6">
                    <label>Country</label>
                    <ComAutoComplete v-model="data.country" class="w-full"  placeholder="Country" doctype="Country"  />
                </div>
                <div class="col-6">
                    <label>City</label>
                    <InputText v-model="data.city" type="text" class="w-full"  placeholder="City"/>
                </div>
                <div class="col-6">
                    <label>Contact Name</label>
                    <InputText v-model="data.contact_name" type="text" class="w-full"  placeholder="Contact Name"/>
                </div>
                <div class="col-6">
                    <label>Phone Number</label>
                    <InputText v-model="data.phone_number" type="text" class="w-full"  placeholder="Phone Number"/>
                </div>
                <div class="col-6">
                    <label>Email</label>
                    <InputText v-model="data.email" type="text" class="w-full"  placeholder="Email"/>
                </div> 
                </div>
                </template>
                </ComReservationStayPanel>
            </div>
            <div class="col-12">
                <ComReservationStayPanel title="Credit Card Information">
                    <template #content>
                <div class="grid">
                    <div class="col-6">
                        <label>Bank Name</label>
                        <InputText v-model="data.bank_name" type="text" class="w-full"  placeholder="Bank Name"/>
                    </div>
                    <div class="col-6">
                        <label>Credit Card Number</label>
                        <InputText v-model="data.credit_card_number" type="text" class="w-full"  placeholder="Credit Card Number"/>
                    </div>
                    <div class="col-6">
                        <label>Card Holder Name</label>
                        <InputText v-model="data.card_holder_name" type="text" class="w-full"  placeholder="Card Holder Name"/>
                    </div>
                </div>
                    </template>
                </ComReservationStayPanel>
            </div>
        </div>   
        
    
    </ComDialogContent>

</template>
<script setup>
import { ref, createUpdateDoc,inject,getDoc,onMounted } from '@/plugin'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject('dialogRef')
const data = ref({})
const loading = ref(false)
const socket = inject("$socket")
const property = JSON.parse(localStorage.getItem("edoor_property"))

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
function onClose(){
    dialogRef.value.close()
}
function onSave(){
    loading.value = true
    const rename = {
        old_name: dialogRef.value.data.name,
        new_name: data.value.business_source
    }
    createUpdateDoc("Business Source", {data: data.value}, '', rename).then((r)=>{
        socket.emit("RefreshData", {property:property.name,action:"refresh_business_source"});
        dialogRef.value.close(rename.new_name)
        
    }).catch((err)=>{
        loading.value = false
    })
}
onMounted(() => {
  if(dialogRef.value.data.name){
    onLoad()
  }else{
    data.value.property = property.name
  }
})
</script>