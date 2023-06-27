<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="grid">
            <div class="col">
                <label>Stay Guest</label><br/>
                <ComSelect class="mb-3 w-full" v-model="doc.guest" :options="guests" optionLabel="guest_name" optionValue="name" :clear="false" />
            </div>
            <div class="col-8">
                <label hidden>Note</label><br/>
                <InputText placeholder="Note" class="w-full" type="text" v-model="doc.note" />
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted, } from "@/plugin"
const dialogRef = inject("dialogRef");
const frappe = inject('$frappe');
const db = frappe.db();
const isSaving = ref(false)
const doc = ref({})
const reservation_stay = ref({})
const guests = ref([])

function onSave() {

    isSaving.value = false;
    db.createDoc('Reservation Folio', doc.value)
        .then((doc) => {
            dialogRef.value.close(doc)
        })
}


onMounted(() => {
    reservation_stay.value = dialogRef.value.data.reservation_stay
    doc.value.reservation_stay = reservation_stay.value.name
    doc.value.guest = reservation_stay.value.guest
    let data = []
    guests.value.push({
        name: reservation_stay.value?.guest,
        guest_name: reservation_stay.value?.guest_name,
    })
    reservation_stay.value.additional_guests.forEach(r => {
        guests.value.push({
            name: r.guest,
            guest_name: r.guest_name
        })

    });


});


</script>