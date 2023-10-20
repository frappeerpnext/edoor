<template>
    <ul>
        <template v-for="(s, index) in rs.reservationFolioList" :key="index">
            <li>
                {{ s.name }} | {{ s.guest_name }} | {{ s.balance }} {{ s.reservation_status }} | {{ s.status_color }} | {{
                    s.rooms }}
                <ul>
                    <li v-for="(d, index) in s.folios" :key="index">
                        <Button @click="onSelectFolio(d)" v-if="d.selected" style="background-color: red;">
                            {{ d.name }} | {{ d.posting_date }} | {{ d.guest_name }} | {{ d.balance }} | selected :{{
                                d.selected }} | Is Master:{{ d.is_master }} <br />
                            Balance:{{ d.balance }}
                        </Button>
                        <Button @click="onSelectFolio(d)" v-else>
                            {{ d.name }} | {{ d.posting_date }} | {{ d.guest_name }} | {{ d.balance }} | selected :{{
                                d.selected }} | Is Master:{{ d.is_master }}
                            <br />
                            Balance:{{ d.balance }}
                            Status: {{ d.status }}
                        </Button>

                    </li>
                </ul>

                <Button @click="onAddNewFolio(s)">Add New Folio</Button>
            </li>
        </template>
    </ul>
</template>
<script setup>
import {  inject, useDialog } from '@/plugin';
import ComNewReservationStayFolio from '@/views/reservation/components/reservation_stay_folio/ComNewReservationStayFolio.vue';

const dialog = useDialog();
const rs = inject("$reservation")
const emit = defineEmits(["onSelectFolio"])

 

function onSelectFolio(f) {
    clearSelectedFolio()
    f.selected = true


    emit("onSelectFolio", f)
}
function clearSelectedFolio() {
    const selected = rs.reservationFolioList.map(r => r.folios).flat().find(x => x.selected == true)
    if (selected) {
        selected.selected = false
    }

}

function onAddNewFolio(stay) {
    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
            folio: {
                guest: stay.guest,
                reservation: stay.reservation,
                reservation_stay: stay.name,
                property: window.property_name
            },
        },
        props: {

            header: 'Create New Folio',
            style: {
                width: '50vw',
            },
            modal: true,
            position: 'top',
            closeOnEscape: false
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {

                loadReservationFolioList(data.name)
            }
        }
    })
}


</script>