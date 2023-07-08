<template>
    <div>
         
        <SplitButton class="border-split-none" label="Mores" icon="pi pi-list" :model="items" />
        <Button class="conten-btn" icon="pi pi-chevron-down" iconPos="right" type="button" label="Mores"
        @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
        <Menu ref="folio_menu" id="folio_menu" :popup="true">
            <template #end>
                <button @click="onMarkAsMasterRoom()"
                    v-if="rs.reservationStay.is_master==0 && (rs.reservationStay.reservation_status =='Reserved' || rs.reservationStay.reservation_status =='In-house')"
                    class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                    <i class="pi pi-file-edit" />
                    <span class="ml-2">Mark as Master Room </span>
                </button>
            </template>
        </Menu>
    </div>

</template>
<script setup>
import { inject ,ref ,useConfirm,useToast,postApi } from "@/plugin";
import ComAuditTrail from '../../../components/layout/components/ComAuditTrail.vue';
const socket = inject("$socket")
const confirm = useConfirm()
const toast = useToast();
const emit = defineEmits('onAuditTrail')
const items=ref([])
const folio_menu = ref();
const rs = inject("$reservation_stay")
const toggle = (event) => {
    folio_menu.value.toggle(event);
}
items.value.push({
    label: "Audit Trail",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
items.value.push({
    label: "Allow post to City Ledger",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
items.value.push({
    label: "Edit Trail",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})
items.value.push({
    label: "Edit Trail",
    icon: 'pi pi-history',
    command: () => {
    emit('onAuditTrail')
    }
})


function onMarkAsMasterRoom(){
    confirm.require({
        message: 'Are you sure you want to mark this room as master room?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            postApi("reservation.mark_as_master_folio",{
                reservation:rs.reservation.name,
                reservation_stay:rs.reservationStay.name
            }).then((doc)=>{
                
                rs.reservationStay = doc.message
                socket.emit("RefreshReservationDetail",rs.reservation.name)
                
                //toast.add({ severity: 'info', summary: 'Information', detail: 'Update successfully', life: 3000 });
            })
            
        },
        
    });
}

</script>