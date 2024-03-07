<template>
    <div> 
        <Button icon="pi pi-ellipsis-v text-lg text-700 more-btn-note" class="w-2rem h-2rem" text rounded aria-label="setting" aria-haspopup="true" aria-controls="manu_btn" @click="toggle" />
        <template v-if="data?.name">
            <Menu ref="show" :id="data?.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end>
                    <button @click="onEdit()" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround" >
                        <i class="pi pi-pencil me-1"></i>
                        <span class="ml-2">
                            {{ $t('Edit') }}
                            </span>
                    </button>
                    <button @click="onDelete()" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        <i class="pi pi-trash  me-1"></i>
                        <span class="ml-2">
                            {{ $t('Delete') }}
                            </span>
                    </button>
                </template>
            </Menu>
        </template>
    </div>
</template>
<script setup>
    import {ref, useConfirm,deleteDoc,inject,useToast } from "@/plugin";
    import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
    const gv = inject('$gv');
    const confirm = useConfirm()
    const toast = useToast()
    const props = defineProps({
        data: Object
    })
    const loading = ref(false)
    const emit = defineEmits(['onEdit','onDeleted'])
    const show = ref()
    const deleteNote = ref()
    const { getTotalNote } = inject('get_count_note')
    const toggle = (event) => {
        show.value.toggle(event);
    };
    function onEdit(){
        emit('onEdit', props.data.name)
    }
    function onDelete (){
        if(!gv.cashier_shift?.name){
        toast.add({ severity: 'warn', summary: "There is no cashier open. Please open your cashier shift", life: 3000 })
    return 
	}
        confirm.require({
        message: 'Are you sure you want to delete reservation note?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
             deleteDoc('Comment',props.data.name )
                 .then(() =>{
                    deleteNote.value = props.data.name
                    emit('onDeleted')
                    getTotalNote()
                    loading.value = true

                 } )               
        },
    });
    }
</script>
<style lang="">
    
</style>