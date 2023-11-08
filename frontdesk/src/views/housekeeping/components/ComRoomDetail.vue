<template>
   <ComDialogContent hideButtonOK :hideButtonClose="false" @onClose="onClose" :loading="loading">
        <div class="iframe-view guest-detail">
            HIII
            {{ name }}
            {{ room }}
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted,computed,useDialog ,getDocList} from '@/plugin'
const dialogRef = inject("dialogRef")
const name = ref("")
const data = ref([]);
onMounted(() => {
    name.value = dialogRef.value.data.name
    let dataFilter = [
        'name','=',name.value
    ]
    getDocList('Room', {
        fields: ["name"],
        filters: dataFilter,
        limit: 20,
limit_start: 0,
as_dict: true
    }).then((r)=>{
        data.value = r
    }).catch((err)=>{
      
    })
})
</script>
