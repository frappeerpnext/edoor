<template>   
    <div> 
        <div v-if="total_notification>0" style="padding: 0.6rem 0.65rem;margin-top: 3px;">
            <i  @click="toggle" v-badge="total_notification" class="pi pi-bell cursor-pointer text-white" style="font-size:18px" />
        </div>
        <div v-else style="padding: 0.6rem 0.65rem;margin-top: 3px;">
            <i class="pi pi-bell cursor-pointer text-white" @click="toggle" style="font-size:18px" />
        </div>
         
    </div>


    <OverlayPanel ref="op">
        <div class="w-25rem h-30rem overflow-auto" >
            <div class="flex flex-column ">
                <template v-if="data.length>0">
                        <template v-for="(d, index) in data" :key="index"> 
                            <Button :class="d.read==0?'bg-indigo-100':''" class="p-0 bg-transparent text-black-alpha-90 w-full text-left border-none flex w-full py-2 px-2 hover:bg-indigo-100 my-1 white-space-nowrap" @click="onViewNotificationDetail(d)">
                                <div class="flex gap-2">
                                    <div class="flex gap-2">
                                        <div v-if="d.read==0" class="text-6xl text-green-500">&#183;</div>
                                        <div class="flex align-items-center h-full">
                                            <Avatar :label="avatar_letter" class="mr-2 " size="large" style="background-color: #ece9fc; color: #2a1261;border-radius: 50% !important;" shape="circle" />
                                        </div>
                                    </div>
                                    <div>
                                        <div class="ellipsis-3-lines">{{ d.subject }}</div>
                                        <i style="font-size: 10px;"><ComTimeago :date='d.modified' /></i>
                                    </div>
                                </div> 
                            </Button> 
                        </template>
                </template> 
                <template v-else>
                    <div class="h-30rem align-items-center text-center flex justify-content-center align-content-center h-full">
                       
                        <div> 
                            <div>
                                 <i class="pi pi-bell text-6xl" />
                            </div>
                           
                            <strong>{{$t('No Notification')}}</strong>
                    <p>
                        {{$t(`There's no notification for you`)}}
                    </p>    
                        </div>
                      
                    </div>
                </template>
            </div>
        </div>
        <Button v-if="data.length>0" class="d-bg-set btn-inner-set-icon border-none mt-3" @click="onViewAllNotification">View All Notifications</Button>
    </OverlayPanel>

</template>
<script setup> 
import { ref,getDocList,getCount,onMounted ,useDialog, inject} from "@/plugin"
import ComNotificationDetail from "@/views/notification/ComNotificationDetail.vue"
import ComNotificationList from "@/views/notification/ComNotificationList.vue"
import { i18n } from '@/i18n';

const { t: $t } = i18n.global;
const moment= inject("$moment")
const dialog = useDialog()
const op = ref();
const data = ref([])
const total_notification = ref(0)
const avatar_letter = ref('')
const toggle = (event) => {
    op.value.toggle(event);
    if (data.value.length==0){
     
        getData()
    }
}

function getData(){
    getDocList("Notification Log",{
        fields:["*"],
        filters:[["for_user","=",window.user.name],["document_type","not in",["Email Queue"]]]
    }).then(result=>{
        data.value = result.sort((a, b) => a.read - b.read)
        data.value.forEach(element => {
            avatar_letter.value = element.modified_by.charAt(0).toUpperCase()
        });
    })
}

function getCountData(){
  
    getCount("Notification Log", 
     [["for_user","=",window.user.name],["read","=",0],["document_type","not in",["Email Queue"]]]
    ).then(result=>{
        total_notification.value = result
       
    })
}

function onViewNotificationDetail(data) {
    const dialogRef = dialog.open(ComNotificationDetail, {
    data:data,
    props: {
        header: $t('Notification Detail'),
      contentClass: 'ex-pedd',
      style: {
        width: '80vw',
          },
    maximizable: true,
      modal: true,
      position: 'top',
      closeOnEscape: false,
      breakpoints:{
                '960px': '90vw',
                '640px': '100vw'
            },
    },
    onClose: (options) => {
    
    }
  })
}

function onViewAllNotification(){
 
    dialog.open(ComNotificationList, {
    
    props: {
      header: 'All Notification',
      style: {
        width: '75vw',
      },
      modal: true,
      position: 'top',
      closeOnEscape: false,
      breakpoints:{
                '960px': '75vw',
                '640px': '100vw'
            },
    },
    onClose: (options) => {
    
    }
  })
}
onMounted(()=>{
    getCountData()
    
})


</script> 
<style scoped>
.ellipsis-3-lines {
    display: -webkit-box;           
    -webkit-line-clamp: 3;           
    -webkit-box-orient: vertical;   
    overflow: hidden;                
    text-overflow: ellipsis;         
    max-height: calc(1.5em * 3);    
    white-space: break-spaces;        
}</style>