<template>
<ComDialogContent hideButtonClose @onOK="onSave" :loading="loading">
<div class="flex align-items-center relative gap-2">
    <label for="allowmaster" class="font-medium cursor-pointer ">{{ $t('Show Room Rate') }}
        </label>
    <Checkbox
        v-tippy="$t('If you tick this check box, That Will Show Room Rate in Guest Folio Invoice')"
        v-model="data.show_room_rate_in_guest_folio_invoice" :binary="true" :trueValue="1"
        inputId="allowmaster" :falseValue="0" />
      
       
</div>  
</ComDialogContent>
</template>
<script setup>
  import {ref, getApi,postApi,onMounted,inject,useConfirm,updateDoc} from "@/plugin"
  const confirm = useConfirm()
  import {i18n} from '@/i18n';
  const { t: $t } = i18n.global;
  const loading = ref(false)
  const dialogRef = inject("dialogRef");
    const data = ref({
        show_room_rate_in_guest_folio_invoice : 0
    })

    function onSave(){
        loading.value = true
        if (data.value.reservation) {
            updateDoc('Reservation', data.value.reservation ,{
                show_room_rate_in_guest_folio_invoice : data.value.show_room_rate_in_guest_folio_invoice
            })
                .then((newdoc) => {
                    loading.value = false
                    dialogRef.value.close(true)
                     window.postMessage({action:"ReservationDetail"},"*")
                window.postMessage({action:"ReservationStayDetail"},"*")
                
                }).catch((err) => {
                    loading.value = false
                    })
        }
    }
    onMounted(()=>{
        data.value = dialogRef.value.data
    })
</script>