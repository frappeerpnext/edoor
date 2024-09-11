<template>
    <ComDialogContent  @onOK="onSave" titleButtonOK="Save Setting" :loading="isSaving" hideButtonClose>
        <div class="flex-auto">
            <label  class="font-bold block mb-2"> {{$t("Set day increment for next/previous navigation.")}} </label>
            <InputNumber v-model="setting.increasement_day"    showButtons :min="1" :max="7" />
 
        </div>
        <div class="flex-auto mt-4">
            <label  class="font-bold block mb-2"> {{$t("Show/Hide Unassign Room")}} </label>
            <Checkbox input-id="rate_tax" class="w-full flex "
                                v-model="setting.show_unassign_room" :binary="true" :trueValue="1" :falseValue="0"  />
 
        </div>

</ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted} from "@/plugin"
import {i18n} from '@/i18n';

import { useDialog } from 'primevue/usedialog';
const dialog = useDialog();
const { t: $t } = i18n.global; 

const dialogRef = inject("dialogRef");

const setting = ref({increasement_day:3})
function onSave() {
     
    localStorage.setItem("room_inventory_setting", JSON.stringify(setting.value))
    dialogRef.value.close(true)
}
  
onMounted(() => {
    const local_setting = localStorage.getItem("room_inventory_setting")
    if (local_setting){
        setting.value = JSON.parse(local_setting)
    }

});


</script>