<template>
  <ul>
    <li v-for="(n, index) in all_notes" :key="index">
      <div v-html="n.note"></div>
      <button @click="EditNote(n)">Edit</button><br>
      <button @click="DeleteNote(n)">Delete Note</button>
    </li>
  </ul>
  <hr>
  <input type="text" v-model="note" />
  <button @click="AddNote">Add Note</button>
  <hr>

  <textarea v-model="note_object.note" rows="10" style="width:650px" />
  {{ note_object.name }}
  <button @click="UpdateNote">Update Note</button>
</template>
<script setup>
import { inject, ref } from '@/plugin';
const frappe = inject("$frappe")
const db = frappe.db()

const all_notes = ref([])
const note = ref("")
const note_object = ref({})

db.getDocList("Housekeeping Room Note", {
  fields: ["name", "note"]
})
  .then((data) => {
    all_notes.value = data
  })
  .catch((err) => {
    alert("Load data fail")
  })

function AddNote() {
  db.createDoc('Housekeeping Room Note', {
    room_id: "RM-0004",
    note: note.value
  })
    .then((doc) => {
      all_notes.value.push(doc)
    })
}

function EditNote(n) {

  note_object.value = n
}

function UpdateNote() {
  db.updateDoc('Housekeeping Room Note', note_object.value.name, {
    note: note_object.value.note
  })
    .then((doc) => console.log(doc))
    .catch((error) => console.error(error));

}

function DeleteNote(n) {
  alert(n.name)
  db.deleteDoc('Housekeeping Room Note', n.name)
    .then((response) => console.log(response.message)) // Message will be "ok"
    .catch((error) => console.error(error));

}

</script>