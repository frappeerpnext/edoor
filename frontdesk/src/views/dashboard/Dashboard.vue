<template>
    <ProgressBar v-if="isLoading" mode="indeterminate" style="height: 6px"></ProgressBar>
    <br/>
 
 
 <Button label="Today" @click="onShowTodayData()" />
  <Button label="Tomorrow" @click="onShowTommorowData()" /> 
  <Calendar v-model="date" @date-select="onDateSelect" dateFormat="dd-mm-yy"/>
 
<h1>Dashboard</h1>
{{  data }} 
{{ moment(data.working_date).format("dddd") }}
{{ moment(data.working_date).format("MMMM") }}
{{ moment(data.working_date).format("DD") }}
{{ moment(data.working_date).format("yyyy") }}
<table border="1">
    <tr>
        <td style="width: 800px;text-align: center; font-size: 24px;">Arrival ({{ data.arrival }})</td>
        <td style="width: 800px;text-align: center; font-size: 24px;">Departure ({{ data.departure }})</td>
    </tr>

    <tr>
        <td>
<iframe  style="height: 500px;margin-top: 5px;" width="100%" :src="arrivalUrl"></iframe>
        </td>
        <td>
     
<iframe style="height: 500px;margin-top: 5px;" width="100%" :src="departureUrl"></iframe>
        </td>
    </tr>
</table>
<DynamicDialog  />
</template>
<script setup>
    
    import Calendar from 'primevue/calendar';
    import ProgressBar from 'primevue/progressbar';
    
    import { inject,ref, onUnmounted } from '@/plugin'
    import GuestDetail from "@/views/guest/GuestDetail.vue"

    const moment = inject("$moment")
    import { useToast } from "primevue/usetoast";
    const toast = useToast();
    
    import { useDialog } from 'primevue/usedialog';
 
    const dialog = useDialog();


    const api = inject('$frappe')
    const data = ref({})
    const date = ref(null)
    const selected_date = ref(null)
    const arrivalUrl = ref("");
    const departureUrl = ref("");
    const isLoading = ref(false)
    const setting = JSON.parse( localStorage.getItem("setting"))
    const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" +  setting.backend_port;
 

    function getArrivalUrl(){
        let url = serverUrl + "/printview?name=" + localStorage.getItem("current_property") + "&doctype=Business Branch&format=eDoor%20Dashboard%20Arrival%20Guest&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
        url = url + "&working_date=" + selected_date.value
        return url;
        
    }

    function getDepartureUrl(){
        let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + localStorage.getItem("current_property") + "&format=eDoor%20Dashboard%20Departure%20Guest&no_letterhead=1&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui"
        url = url + "&working_date=" + selected_date.value
        return url;
        
    }

    function onShowTodayData(){
     
        selected_date.value = data.value.working_date
        date.value =moment(data.value.working_date).format("DD-MM-YYYY")
        arrivalUrl.value = getArrivalUrl();
        departureUrl.value = getDepartureUrl()
        getData()
    }

    
    function onShowTommorowData(){
        const today = moment(data.value.working_date);
        const tomorrow = today.add(1, 'days');
        
        selected_date.value = tomorrow.format("YYYY-MM-DD")
        date.value =tomorrow.format("DD-MM-YYYY")
        arrivalUrl.value = getArrivalUrl();
        departureUrl.value = getDepartureUrl()
        getData()
    }

    function onDateSelect(event){
      
        selected_date.value =  moment(event).format("YYYY-MM-DD")
        arrivalUrl.value = getArrivalUrl();
        departureUrl.value = getDepartureUrl()
        getData();
    }

    getData();


    function getData(){
        isLoading.value = true;
        const call = api.call();
        call.get('edoor.api.frontdesk.get_dashboard_data',{
            property:localStorage.getItem("current_property"),
            date:selected_date.value
        })
        .then((result) => 
        {
            
            data.value = result.message

            if(!selected_date.value){ 
                date.value =moment(data.value.working_date).format("DD-MM-YYYY")
                selected_date.value = data.value.working_date;
                arrivalUrl.value = getArrivalUrl();
                departureUrl.value = getDepartureUrl()
            }
       
            isLoading.value = false;

        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: 'Waring', detail:error.exception.split(":")[1], life: 3000 })
            isLoading.value = false;

        });
        }
    
   

function showGuestDetail(name) {
    const dialogRef = dialog.open(GuestDetail, {
        data:{
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}


const actionClickHandler = async function (e) {
    if (e.isTrusted && typeof (e.data) == 'string') {

        const data = e.data.split("|")

        if (data.length > 0) {

            if (data[0] == "view_guest_detail") {
              
               showGuestDetail(data[1])

            }else if (data[0] == "view_reservation_stay_detail") {
                alert(1234)
            }
        }

    }
};


window.addEventListener('message', actionClickHandler, false);



onUnmounted(() => {
    window.removeEventListener('message', actionClickHandler, false);
})



    

</script>