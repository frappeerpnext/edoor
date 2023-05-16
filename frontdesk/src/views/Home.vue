<template>
  <div>
    <h1>Home Page</h1>
    <span class="material-symbols-outlined">settings</span>
    <Button label="Primary" size="small"/>
    <Button @click="Update">Update </Button>
    <Button @click="AddNote">Add Note </Button>
    <a href="http://192.168.10.114:1216/app/sale">Misc Sale</a>
 
  </div>
</template>

<script setup>
import { inject, ref } from '@/plugin'
const frappe = inject('$frappe')
const db = frappe.db()
const call = frappe.call();
const data = ref()


call.get('edoor.api.frontdesk.get_logged_user').then((r)=>{
  console.log(r)
})


 

db.getDoc('Sale', 'SO2023-0007')
  .then((doc) => {
    data.value = doc
  })
  .catch((error) => console.error(error));

function Update() {
  db.updateDoc('Customer', 'C2023-0149', {
    company_name: 'my update company',
    "gender": "Female",
    phone_number: "0125487598"
  })
    .then((doc) => console.log(doc))
    .catch((error) => console.error(error));
}

function AddNote() {
  db.createDoc('Note', {
  title: 'note from vue',
  public:1,
  notify_on_login:1,
  notify_on_every_login:1,
  content: 'this is note form vue',
})
  .then((doc) => console.log(doc))
  .catch((error) => console.error(error));
}

</script>
