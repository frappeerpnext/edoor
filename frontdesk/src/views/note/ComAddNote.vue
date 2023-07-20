<template>

    <!-- <Button label="Add Note" @click="visible = true" /> -->
  <ComDialogContent @onOK="onSave" :loading="loading" @onClose="visible = false">
    <!-- {{ data }} -->
    <div class="grid">
      <div class="col-12">
        <div class="w-6">
         <label for="Note Date">Note Date</label>
        <div class="card flex justify-content-left">
          <Calendar class="w-full p-inputtext-sm depart-arr border-round-xl" v-model="data.note_date"
        :placeholder="correntDate()" :value="correntDate()" dateFormat="dd-mm-yy" showIcon showButtonBar />
        </div>
      </div>
      </div>
      <!-- <div class="col-6">
        <label for="Reference Doctype">Reference Doctype</label>
        <div class="card flex justify-content-left">
        <InputText class="w-full" type="text" v-model="data.reference_doctype" />
        </div>
      </div>
      <div class="col-6">
         <label for="Reference Name">Reference Name</label>
          <div class="card flex justify-content-left">
          <InputText class="w-full" type="text" v-model="data.reference_name" />
          </div>
      </div> -->
      <div class="col-6">
        <label for="Reservation">Reservation</label>
        <div class="card flex justify-content-left">
          <ComAutoComplete class="w-full" v-model="data.reservation" doctype="Reservation"/>
        </div>
      </div>
      <div class="col-6">
         <label for="Reservation Stay">Reservation Stay</label>
         <div class="card flex justify-content-left">
            <ComAutoComplete class="w-full" v-model="data.reservation_stay" doctype="Reservation Stay"/>
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
const note = ref()

function correntDate(){
  if (!data.value.note_date) {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0');
    var yyyy = today.getFullYear();

    today = mm + '-' + dd + '-' + yyyy;
    return today;
  } else {
    return '';
  }
}

function onSave(){
  loading.value = true
  let dataSave = JSON.parse(JSON.stringify(data.value))
  dataSave.note_date = gv.dateApiFormat(dataSave.note_date)
  createUpdateDoc("Frontdesk Note", {data: dataSave}).then((r)=>{
    note.value = r;
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
  }
})

</script>
<style scoped>
.conten-btn:hover{
background: #fbedc2 !important;
}
</style>

