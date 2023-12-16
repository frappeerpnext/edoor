<template>
  <ComDialogContent @onOK="onSave" :loading="loading" @onClose="onClose">
    <div class="grid">
      <div class="col-12">
        <div class="w-6">
         <label for="Note Date">Note Datexx</label>
          <div class="card flex justify-content-left">
            <Calendar :selectOtherMonths="true" class="w-full p-inputtext-sm depart-arr border-round-xl" v-model="data.custom_note_date"
              dateFormat="dd-mm-yy" showIcon showButtonBar selectOtherMonths  panelClass="no-btn-clear"/>
          </div>
        </div>
      </div>
      <div class="col-6"> 
        <label for="reference_documnent">Reference Document</label>
        <ComAutoComplete inputId="reference_documnent" isFull v-model="data.reference_doctype" placeholder="Reference Document" doctype="DocType" 
        :filters="{'name':['in',['Reservation','Reservation Stay','Folio Transaction','Customer','Room Block','Business Source','City Ledger Account','Room']]}"
        @onSelected="onSelectReferenceDocument"
        />
      </div>
      <div class="col-6"> 
        <label for="reference_name">Reference Name</label>
        <ComAutoComplete isFull v-model="data.reference_name" placeholder="Reference Name" :doctype="data.reference_doctype"
        :filters="{ 'property' : property.property }"
        :disabled="!data.reference_doctype"
        />
      </div>
 
 
      <div class="col-12">
        <label>Note</label>
        <div class="card flex justify-content-left">
            <Textarea v-model="data.content" rows="3" autoResize style="width: 100%;" />
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

const property = window.property
const data = ref({
  custom_property : window.property_name,
  custom_posting_date: window.current_working_date,
  custom_is_audit_trail:1,
  custom_note_date:moment().toDate(),
  custom_is_note:1,
  comment_type:'Comment'
})

function onSelectReferenceDocument(d){
  if (!d.value){
    data.value.reference_name =""
  } 
}
function onSave(){
  if(!data.value.content){
    gv.toast('warn','Please input note.')
    return
  }else if(!data.value.reference_name && data.value.reference_doctype ){
    gv.toast('warn','Please Select Reference Name.')
    return
  }
  loading.value = true
  let dataSave = JSON.parse(JSON.stringify(data.value))
  dataSave.custom_note_date = gv.dateApiFormat(dataSave.custom_note_date)
  createUpdateDoc("Comment", dataSave)
  .then((r)=>{
    loading.value = false
    dialogRef.value.close(r)
    window.socket.emit("RoomBlockList",window.property_name)
  }).catch((err)=>{
    loading.value = false 
  })
}

onMounted(() => {
  if(dialogRef.value.data.name){
    getDoc("Comment", dialogRef.value.data.name).then((r)=>{
      data.value = r
      window.socket.emit("RoomBlockList",window.property_name)
    })
  }else{
    data.value.custom_note_date = new Date()
    data.value.property = property.name
  }
})

function onClose(){
    dialogRef.value.close()
}
</script>
