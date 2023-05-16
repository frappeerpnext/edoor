<template>
    REservatio nlist
    {{ data }}
    <table>
        <tr>
            <th>Reservation #</th>
            <th>Ref #</th>
            <th>Guest Name</th>
            <th>Arrival</th>
            <th>Departure</th>
        </tr>
        <tr v-for="(d, index) in data" :key="index">
            <td>{{d.name}}</td>
            <td>{{d.reference_number}}</td>
            <td><a @click="showGuestDetail(d.guest)"> {{d.guest}}</a></td>
            <td>{{d.arrival_date}}</td>
            <td>{{d.departure_date}}</td>
        </tr>
    </table>
    <DynamicDialog  />
</template>
<script setup>
    import { inject,ref, onUnmounted } from '@/plugin'
    import GuestDetail from "@/views/guest/GuestDetail.vue"
    const api = inject('$frappe')

    import { useDialog } from 'primevue/usedialog';
 
    const dialog = useDialog();

    const data = ref([])
    const db = api.db();
    db.getDocList('Reservation',
    {
        fields: ["*"],
    }
    )
    .then((docs) => {
        data.value = docs
    })
    .catch((error) => console.error(error));


    
function showGuestDetail(name) {
    const dialogRef = dialog.open(GuestDetail, {
        data:{
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}



</script>