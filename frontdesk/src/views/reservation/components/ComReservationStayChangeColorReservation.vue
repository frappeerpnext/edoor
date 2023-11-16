<template>
    <ComOverlayPanelContent title="Change Color" :loading="loading" @onSave="onSave" @onCancel="emit('onClose')">
    <div class="card flex justify-content-center">
        <Dropdown  v-model="reservation_color_code" :options="items" optionLabel="name" showClear placeholder="Select Reservation Color Code" class="w-full md:w-21rem" >
            <template #value="slotProps">
        <div v-if="slotProps.value" class="flex align-items-center">
            <div :style="'height: 20px;width: 20px;border-radius: 10px;margin-right: 8px;background:' + slotProps.value.color"></div>
            <div  >{{ slotProps.value.name }}</div>
        </div>
        <span v-else>
            {{ slotProps.placeholder }}
        </span>
    </template> 
    <template #option="slotProps">
        <div class="flex align-items-center">
            <div :style="'height: 20px;width: 20px;border-radius: 10px;margin-right: 8px;background:' + slotProps.option.color"> </div>
            <div  >{{ slotProps.option.name }}</div>
        </div>
    </template>
        </Dropdown>

    </div>
    <div class="col flex gap-3" >
        <Checkbox v-model="checked" :binary="true" :trueValue = "1" :falseValue = "0"/>
        <label> Apply to all reservation</label>
    </div>
   
    </ComOverlayPanelContent> 
</template>     
<script setup>
import { ref, inject,getDocList, onMounted,postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const emit = defineEmits(['onClose'])
const rs = inject('$reservation_stay');
const gv = inject('$gv');
const loading = ref(false)
const checked = ref(0);
const items = ref([]);

const reservation_color_code = ref()

function onSave() {
    if (!rs.reservationStay.is_active_reservation) {
        gv.toast('warn', 'Cannot change color on an inactive reservation.')
        return
    }

    loading.value = true;

    const stay = {
        name: rs.reservationStay.name,
        reservation_color: reservation_color_code.value ? reservation_color_code.value.color : '',
        reservation_color_code: reservation_color_code.value ? reservation_color_code.value.name : '',
        apply_to_all_reservation: checked.value !== undefined ? checked.value : null,
    };

    postApi('reservation.update_reservation_stay_color', { data: stay })
        .then((r) => {
            rs.reservationStay = r.message;
            loading.value = false;
            window.socket.emit('ReservationStayDetail', { reservation_stay: window.reservation_stay });
            window.socket.emit('Frontdesk', window.property_name);
            emit('onClose');
        })
        .catch(() => {
            loading.value = false;
            gv.toast('error', 'Failed to update reservation color.');
        });
}



onMounted(() => {
    getDocList("Reservation Color Code", {
        fields: ["name", "color"],
        limit: 1000
    }).then(data => {
        items.value = data;
        // Check if reservation color code is present; if not, set the value to null
        if (!rs.reservationStay.reservation_color_code) {
            reservation_color_code.value = null;
        } else {
            reservation_color_code.value = {
                name: rs.reservationStay.reservation_color_code,
                color: rs.reservationStay.reservation_color
            };
        }
    });
});

</script>
