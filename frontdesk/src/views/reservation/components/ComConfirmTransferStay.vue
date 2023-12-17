<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Ok" :hideIcon="false" :loading="loading">
        
        <div>

            <label for="target_reservation" class="mb-1 font-medium block">Target Reservation</label>
            <ComAutoComplete class="w-full" placeholder="Select target reservation" v-model="data.target_reservation" doctype="Reservation" :filters="{ 'property': property_name,reservation_status:['in',['Checked Out','Reserved','Confirmed','In-house']],departure_date:['>',working_date], name:['!=',data.source_reservation]}"/>
        </div>
                <label for="reason-text" class="mb-1 font-medium block">Reason</label>
        <Textarea autofocus v-model="data.note" id="reason-text" rows="3" cols="50" placeholder="Please Enter Reason" class="w-full" />


        

    </ComDialogContent>
</template>
<script setup>
import { useToast, ref, onMounted, inject, postApi} from '@/plugin'


const toast = useToast();

const dialogRef = inject("dialogRef");
const property_name = window.property_name
const working_date = window.current_working_date

const emit = defineEmits(['onOk', 'onClose'])

const data = ref({keep_rate:1})
 
const loading = ref(false)


function onOk() {
    if (!data.value.note) {
        toast.add({ severity: 'warn', summary: 'Enter Note', detail: "Please Enter Note", life: 3000 })
        return
    }
    if (!data.value.target_reservation) {
        toast.add({ severity: 'warn', summary: '', detail: "Please select target reservation", life: 3000 })
        return
    }
    loading.value = true

 

    loading.value = true
    
    postApi("group_operation.group_transfer_stay_to_other_reservation",
    {
        data:data.value
    }
    ).then(result=>{
        loading.value = false
        //load reservation will do after this modal is closed

        dialogRef.value.close(true);

    }).catch(ex=>{
        loading.value = false
    })

   

}

 
onMounted(() => {
    data.value = dialogRef.value.data;
})




</script>
<style lang="">
    
</style>