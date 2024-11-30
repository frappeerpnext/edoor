<template>
    <ComDialogContent @onOK="onEdit"  hideButtonOK :loading="isSaving" @onClose="onClose">
    <div class="grid p-2">
        <div class="py-2 mt-1 border-1  bg-slate-200 font-medium ps-4 w-full flex justify-content-between pe-2 align-items-cente">
            <div class="pt-1">
            {{ $t('Detail of ') }} {{ data.name }} - 
            <span  class="px-2 text-white border-round-xl" :style="{background:data.status == 'Lost' ? 'red' : 'blue' }">
                {{ data.status }} 
            </span>
            <span v-if="data.is_taken" class="px-2 text-white border-round-xl bg-cyan-400 ms-3" >
                Taken
            </span>
             </div>
             <div>
                <Button  class="border-none h-2rem" icon="pi pi-pencil text-sm"
                :label=" $t('Edit') " @click="onEdit" />
             </div>
        </div>
        <table class="w-full">
            <ComStayInfoNoBox label="Posting Date" :value="data.posting_date" />
            <ComStayInfoNoBox label="Location" :value="data.location" />
            <ComStayInfoNoBox label="Status" :value="data.status" />
           
        </table>

        <div class="h-10rem w-full p-2 bg-red border-1">
                {{ data.note }}
        </div>
    </div>
    <hr class="my-2" />
    <div v-if="data.is_taken" class="grid p-2">
        
        <div class="py-2 mt-1 border-1  bg-slate-200 font-medium ps-4 w-full flex justify-content-between pe-2 align-items-center">
            <div>
                {{ $t('Detail Taken') }}
            </div>
            
            <div>
                <Button  class="border-none h-2rem" icon="pi pi-pencil text-sm"
                :label=" $t('Edit') " @click="onTaken" />
            </div>
        </div>
        <table class="w-full">
            <ComStayInfoNoBox label="Taken Date" :value="data.taken_date" />
            <ComStayInfoNoBox label="Taken By" :value="data.taken_by" />
        </table>

        <div class="h-10rem w-full p-2 bg-red border-1">
                {{ data.taken_note }}
        </div>
    </div>
    <div class="">
        <ComDocument v-if="dataImage" @updateCount="loadData" doctype="Lost and Found"
                    :doctypes="['Lost and Found']" :showDoc="false" :attacheds="[data?.name]" :docname="data?.name" />
    <Galleria v-model:activeIndex="activeIndex" v-model:visible="displayCustom" :value="dataImage" :responsiveOptions="responsiveOptions" :numVisible="7"
            containerStyle="max-width: 850px" :circular="true" :fullScreen="true" :showItemNavigators="true" :showThumbnails="false">
            <template #item="slotProps">
                <img :src="slotProps.item.file_url" style="width: 100%; display: block" />
            </template>
            <template #thumbnail="slotProps">
                <img :src="slotProps.item.file_url" style="display: block" />
            </template>
        </Galleria>
     <div v-if="dataImage" class="grid grid-cols-12 mt-2" >
            <div v-for="(image, index) of dataImage" :key="index" class="col-3 relative border-1 flex justify-content-center">
                <img :src="image.file_url" class="h-20rem" style="cursor: pointer" @click="imageClick(index)" />
                <Button  class="border-none absolute bottom-2 right-2 bg-red-500 text-white" icon="pi pi-trash text-sm"
               @click="onDelete(image.name)" />
            </div>
        </div>
    </div>
    <template #footer-right>
        <Button v-if="!data.is_taken"  class="border-none" icon="pi pi-check text-sm"
        :label=" $t('Taken') " @click="onTaken" />
    </template>
  
  
</ComDialogContent>
</template>
<script setup >
import { ref, inject, getDoc,getDocList, onUnmounted, onMounted ,useDialog , useConfirm , deleteDoc} from '@/plugin';
import FileUpload from 'primevue/fileupload';
import ComTaken from "@/views/lost_and_found/components/ComTaken.vue";
import Galleria from 'primevue/galleria';
import ComeditLostAndFound from "@/views/lost_and_found/components/ComeditLostAndFound.vue";
const dialogRef = inject('dialogRef');
const dialogConfirm = useConfirm();
const loading = ref()
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog()
const data = ref({})
const dataImage = ref({})
const activeIndex = ref(0);
const responsiveOptions = ref([
    {
        breakpoint: '1024px',
        numVisible: 5
    },
    {
        breakpoint: '768px',
        numVisible: 3
    },
    {
        breakpoint: '560px',
        numVisible: 1
    }
]);
const displayCustom = ref(false);

const imageClick = (index) => {
    activeIndex.value = index;
    displayCustom.value = true;
};
function loadData() {
    loading.value = true
    getDoc("Lost and Found", dialogRef.value.data.name).then((r) => {
        data.value = r
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
    getDocList("File", {
        fields: ["name","file_url"],
        filters:[[
           "attached_to_name","=" , dialogRef.value.data.name 
        ]]
            
      
    }).then((r) => {
        dataImage.value = r
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })


}
function onClose(){
    dialogRef.value.close()
}
function onTaken() { 
     if(window.isMobile){
    const elem = document.querySelector(".p-dialog");
		elem?.classList.add("p-dialog-maximized"); // adds the maximized class

 }
    dialog.open(ComTaken, {
        data: data.value,
        props: {
            header: $t('Token') + "-" + data.value.name,
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
       
        }
    })
     
}
function onEdit(){
    if(window.isMobile){
    const elem = document.querySelector(".p-dialog");
		elem?.classList.add("p-dialog-maximized"); // adds the maximized class

 }
    dialog.open(ComeditLostAndFound, {
        data: data.value,
        props: {
            header: $t('Token') + "-" + data.value.name,
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
       
        }
    })
}
const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="LostAndFoundList"){
            setTimeout(()=>{
              loadData(false)
            },1000)
            
        }
    };
} 
onMounted(() => {
    loadData()
    window.addEventListener('message', actionRefreshData, false);

});
onUnmounted(() => {
  window.removeEventListener('message', actionRefreshData, false)
})
function onDelete(name){
dialogConfirm.require({
    message: $t('Do you want to delete this record?'),
    header: $t('Delete Confirmation'),
    icon: 'pi pi-info-circle',
    acceptClass: 'border-none crfm-dialog',
    rejectClass: 'hidden',
    acceptIcon: 'pi pi-check-circle',
    acceptLabel: 'Ok',
    accept: () => {
        deleteDoc('File', name).then((doc) => {
            loadData()

        }).catch((err) => {
        })
    }
})
}
</script>