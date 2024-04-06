<template>
    <div class="col-fixed relative pl-0 pr-0 py-0" :style="`width: ${panelWidth ? panelWidth : '250px'}`">
 
        <div class="flex flex-column justify-content-between h-full res-stay-folio-btn-site-bg">
            <div :style="rs.is_page == true ? 'margin-bottom: 1px;' : 'margin-bottom: 60px;'">
                <div class="flex justify-content-between align-items-center p-2">
                    <span>{{ $t('Room Folio') }} </span>
                    <Button class="btn-add-folio" @click="onAddCreatNewFolio"  v-tippy="$t('Create Folio')">
                        <img :src="plus_svg" style="height: 13px;">
                    </Button>
                </div>
                <template v-if="rs.folios && rs.folios.length > 0">

                    <Button :severity="item.selected ? 'folio-active' : 'primary'"
                        v-for="(item, index) in Enumerable.from(rs.folios).orderByDescending('$.is_master').toArray()"
                        :key="index" @click="onClick(item)" class="flex w-full btn-folio-name mr-1" style="z-index: 1;">
                        <span v-if="item.is_master == 1"><img :src="crown_svg" class="folio-is-mater-icon me-2"
                                style="height: 13px;"></span>
                        <span class="flex flex-column align-items-start w-full">
                            <span class="flex justify-content-between w-full">
                                <span class="line-height-2">{{ item.name }}</span>
                                <span v-if="can_view_rate" class="line-height-2">
                                    <CurrencyFormat :value="item.balance" class="white-space-nowrap" />
                                </span>
                            </span>
                            <span class="flex justify-content-between w-full">
                                <span class="flex text-left line-height-2">
                                    <span style="display:inline-block;max-width: 95px;" v-tippy="item.guest_name" class="white-space-nowrap text-gray-600 line-height-2 
                                        text-sm folio-remark cus me-1 overflow-hidden text-overflow-ellipsis">
                                        <img :src="guest_svg" style="display:inline-block; width: 10px; margin:-2px -2px 0 0;">
                                        <span class="ms-1">{{ item.guest_name }}</span>
                                    </span>
                                    <span style="display:inline-block;"
                                        class="text-sm folio-remark closed me-1"
                                        v-if="item.status == 'Closed'"> {{ $t('Closed') }} </span>
                                    <span style="display:inline-block;"
                                        class="text-sm folio-remark me-1"
                                        v-else> {{$t('Open')}} </span>
                                </span>
                                <span class="flex align-items-end h-full">
                                    <span class="text-xs">
                                        {{ moment(item.creation).format("DD-MM-YYYY") }}
                                    </span>
                                </span>
                            </span>
                        </span>
                    </Button>
                </template>
            </div>

            <div v-if="can_view_rate" :class="rs.is_page == true ? 'flex flex-column bg-white mt-3 page_total_foliolist' : 'flex flex-column bg-white mt-3 relative lg:fixed total_foliolist'" :style="`width: ${panelWidth ? panelWidth : '250px'};bottom:0px;z-index: 1;`">
                <div class="flex justify-content-end align-items-cente border-1 border-red-100 p-2">
                    <div class="pr-3"><label> {{ $t('Total Debit') }} </label></div>
                    <div><span>
                            <CurrencyFormat :value="totalDebit" class="white-space-nowrap font-medium" />
                        </span></div>
                </div>
                
                <div class="flex justify-content-end align-items-cente border-1 border-red-100 border-top-none p-2">
                    <div class="pr-3"><label>{{ $t('Total Credit') }}</label></div>
                    <div><span>
                            <CurrencyFormat :value="totalCredit" class="white-space-nowrap font-medium" />
                        </span></div>
                </div>


                <div class="flex justify-content-end align-items-center border-1 border-red-100 border-top-none p-2">
                    <div class="pr-3"><label>{{ $t('Balance') }}</label></div>
                    <div><span>
                            <CurrencyFormat :value="balance" class="white-space-nowrap font-medium" />
                        </span></div>
                </div>
            </div>

            <div style="background: #CECFD0; width:1px; position: absolute;z-index: 0;
            right: 0;
            height: 100%;">
                <!--Divider-->
            </div>
        </div>

    </div>
</template>
<script setup>
import Enumerable from 'linq';
import { inject , computed} from '@/plugin';
import crown_svg from '@/assets/svg/icon-crown.svg'
import plus_svg from '@/assets/svg/icon-add-plus-sign-purple.svg'
import guest_svg from '@/assets/svg/icon-user-use-sytem.svg'
import { useDialog } from 'primevue/usedialog';
import ComNewReservationStayFolio from './ComNewReservationStayFolio.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
    panelWidth: [String, Number]
})

const emit = defineEmits(["onSelectFolio"])

const rs = inject('$reservation_stay');
const dialog = useDialog();
const moment = inject('$moment')
const can_view_rate= window.can_view_rate;

const totalCredit = computed(()=>{
    return rs.folios.reduce((n, d) => n + (d.total_credit || 0), 0) 
})
const totalDebit = computed(()=>{
    return rs.folios.reduce((n, d) => n + (d.total_debit || 0), 0) 
})

// const balance = computed(()=>{
//     return rs.folios.reduce((n, d) => n + (d.balance || 0), 0) 
// })
const balance = computed(() => {
    return totalDebit.value - totalCredit.value;
});


const { loadReservationStayFolioList } = inject("reservation_stay")

function onClick(f) {

    clearSelectedFolio()
        f.selected = true
        emit("onSelectFolio",f)
}
function clearSelectedFolio() {
    
    const selected = rs.folios.find(x => x.selected == true)
    if (selected) {
        selected.selected = false
    }

}

function onAddCreatNewFolio() {

    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
            guest: rs.reservationStay.guest,
            reservation: rs.reservationStay.reservation,
            reservation_stay: rs.reservationStay.name,
            property: window.property_name
        },
        props: {

            header: $t('Create New Folio'),
            style: {
                width: '50vw',
            },
            modal: true,
            position: 'top',
            closeOnEscape: false,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {

                loadReservationStayFolioList(data.name)
            }
        }
    })

}
</script>