<template>
  <div class="card flex justify-content-center">
    <Button label="Add Note" @click="visible = true" />
    <Dialog v-model:visible="visible" modal header="Add Note" :style="{ width: '50vw' }">
      <ComDialogContent @onOK="onSave" :loading="loading" @onClose="visible = false">
        {{ data }}
        <label for="Note Date">Note Date</label>
        <div class="card flex justify-content-left">
          <Calendar class="p-inputtext-sm depart-arr w-full border-round-xl" v-model="data.note_date"
            placeholder="Note Date" dateFormat="dd-mm-yy" showIcon showButtonBar />
        </div>

        <label for="Reference Doctype">Reference Doctype</label>
        <div class="card flex justify-content-left">
          <InputText type="text" v-model="data.reference_doctype" />
        </div>

        <label for="Reference Name">Reference Name</label>
        <div class="card flex justify-content-left">
          <InputText type="text" v-model="data.reference_name" />
        </div>

        <label for="Reservation">Reservation</label>
        <div class="card flex justify-content-left">
          <ComAutoComplete v-model="data.reservation" doctype="Reservation"/>
        </div>

        <label for="Reservation Stay">Reservation Stay</label>
        <div class="card flex justify-content-left">
          <ComAutoComplete v-model="data.reservation_stay" doctype="Reservation Stay"/>
        </div>

        <label>Content</label>
        <div class="card flex justify-content-left">
          <span class="p-float-label">
            <Textarea v-model="data.content" rows="3" cols="75" />

          </span>
        </div>

      </ComDialogContent>

    </Dialog>

  </div>
</template>
<script setup>
import { ref, createUpdateDoc,inject,getDoc,onMounted } from '@/plugin'
const props = defineProps({
  name: {
    type: String,
    default: "1fb3c65a04"
  }
})
const gv = inject('$gv')
const visible = ref(false);
const loading = ref(false);
const data = ref({})
const note = ref()
function onSave(){
  loading.value = true
  let dataSave = JSON.parse(JSON.stringify(data.value))
  dataSave.note_date = gv.dateApiFormat(dataSave.note_date)
  createUpdateDoc("Frontdesk Note", {data: dataSave}).then((r)=>{
    note.value = r;
    loading.value = false
    visible.value = false
  }).catch((err)=>{
    loading.value = false
  })
}
onMounted(() => {
  if(props.name){
    getDoc("Frontdesk Note", props.name).then((r)=>{
      data.value = r
    })
  }
})
</script>

