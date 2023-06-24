<template>
    <div class="col-fixed pr-0 py-0" style="width: 250px;">
        <div class="h-full res-stay-folio-btn-site-bg">
            <div class="flex justify-content-between align-items-center flex-wrap p-2">
                <span>Room Folio</span>
                <Button class="btn-add-folio" @click="onAddCreatNewFolio" v-tooltip.top="'Create Folio'">
                    <img :src="plus_svg" style="height: 13px;">
                </Button>
            </div>
            <Button :severity="item.name == rs.selectedFolio.name ? 'folio-active' : 'primary'"
                v-for="(item, index) in rs.folios" :key="index" @click="onClick(item)"
                class="flex w-full btn-folio-name mr-1">
                <span v-if="item.is_master == 1"><img :src="crown_svg" class="folio-is-mater-icon me-2"
                        style="height: 13px;"></span>
                <span class="flex flex-column align-items-start">
                    <span class="line-height-2">{{ item.name }}</span>
                    <span class="text-left line-height-2">
                        <span style="display:inline-block;"
                            class="text-gray-600 line-height-2 font-italic text-sm folio-remark cus me-1">
                            <img :src="guest_svg" style="display:inline-block; width: 10px; margin:-2px -2px 0 0">
                            {{ item.guest_name }}
                        </span>
                        <span style="display:inline-block;" class="text-orange-700 line-height-2 font-italic text-sm folio-remark me-1"
                            v-if="item.status == 'Closed'">Closed</span>
                            <span style="display:inline-block;"
                            class="line-height-2 text-green-700 font-italic text-sm folio-remark me-1" v-else>Open</span>
                    </span>
                </span>
            </Button>
        </div>
    </div>

    <div class="col-fixed px-0 res-stay-folio-divider">
        <div></div>
    </div>
</template>
<script setup>
import { inject, useToast } from '@/plugin';
import crown_svg from '@/assets/svg/icon-crown.svg'
import plus_svg from '@/assets/svg/icon-add-plus-sign-purple.svg'
import guest_svg from '@/assets/svg/icon-user-use-sytem.svg'
import { useDialog } from 'primevue/usedialog';
import ComNewReservationStayFolio from './ComNewReservationStayFolio.vue';
const rs = inject('$reservation_stay');
const dialog = useDialog();
const toast = useToast();

function onClick(data) {
    rs.onLoadFolioTransaction(data)
}
function onAddCreatNewFolio() {

    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
            reservation_stay: rs.reservationStay,

        },
        props: {
            header: 'Creat New Folio ',
            style: {
                width: '50vw',
            },

            modal: true
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {
                rs.onLoadReservationFolios(data.name).then(()=>{
                    onClick(data.name)
                })
                toast.add({ severity: 'success', summary: "Creat New Folio", detail: "Creat New Folio successfully", life: 3000 })
            }

        }
    })
}
</script>