<template>
  <ComDialogContent @onOK="onSave" :loading="loading" @onClose="onClose">
    <div class="grid">
      <div class="col-12">
        <div class="w-6">
         <label for="Note Date">Note Date</label>
          <div class="card flex justify-content-left">
            <Calendar class="w-full p-inputtext-sm depart-arr border-round-xl" v-model="data.note_date"
              dateFormat="dd-mm-yy" showIcon showButtonBar selectOtherMonths  panelClass="no-btn-clear"/>
          </div>
        </div>
      </div>
      <div class="col-6"> 
        <label for="Reservation">Reservation</label>
        <div class="card flex justify-content-left"> 
          <ComAutoComplete class="w-full" v-model="data.reservation" doctype="Reservation"/>
        </div>
      </div>
      <div class="col-6">
         <label for="Reservation Stay">Reservation Stay</label>
         <div class="card flex justify-content-left">
            <ComAutoComplete fieldFilter="reservation" :valueFilter="data.reservation" class="w-full" v-model="data.reservation_stay" doctype="Reservation Stay"/>
         </div>
      </div>
      <div class="col-12">
        <label>Note</label>
        <div class="card flex justify-content-left">
            <Textarea v-model="data.content" rows="3"  style="width: 100%;" />
        </div>
      </div>
    </div>

  </ComDialogContent>
</template>
<script setup>
import { ref, createUpdateDoc,inject,getDoc,onMounted } from '@/plugin'
const dialogRef = inject("dialogRef");
const gv = inject('$gv')
const loading = ref(false);
const data = ref({})
const property = JSON.parse(localStorage.getItem("edoor_property"))
function onSave(){
  if(!data.value.content){
    gv.toast('warn','Please input note.')
    return
  }
  loading.value = true
  let dataSave = JSON.parse(JSON.stringify(data.value))
  dataSave.note_date = gv.dateApiFormat(dataSave.note_date)
  createUpdateDoc("Frontdesk Note", {data: dataSave}).then((r)=>{
    loading.value = false
    dialogRef.value.close(r)
  }).catch((err)=>{
    loading.value = false
  })
}
onMounted(() => {
  if(dialogRef.value.data.name){
    getDoc("Frontdesk Note", dialogRef.value.data.name).then((r)=>{
      data.value = r
    })
  }else{
    data.value.note_date = new Date()
    data.value.property = property.name
  }
})

function onClose(){
    dialogRef.value.close()
}
</script>
