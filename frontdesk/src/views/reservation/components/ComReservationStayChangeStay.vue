<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div>
        <ComReservationStayPanel title="Change Stay">
            <template #content> 
            <div class="n__re-custom wp-number-cus overflow-auto lg:overflow-hidden">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pe-2">
                                <label> {{ $t('Start Date') }} <span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label>{{ $t('End Date') }} <span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-center px-2">
                                <label class="text-center"> {{ $t('Nights') }} </label>
                            </th>
                            <th class="text-left px-2">
                                <label>{{ $t('Room Type') }}<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left ps-2">
                                <label>{{ $t('Room Name') }}<span class="text-red-500">*</span></label>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr> 
                            <td class="pe-2">
                                <Calendar inputClass="w-10rem lg:w-full" showButtonBar panelClass="no-btn-clear" class="w-full" showIcon v-model="stay.start_date" selectOtherMonths :disabled="!stay.can_change_start_date"  :min-date="minStartDate" @update:modelValue="onStartDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="px-2"> 

                                <Calendar inputClass="w-10rem lg:w-full" panelClass="no-btn-clear" showButtonBar class="w-full" showIcon v-model="stay.end_date" selectOtherMonths :min-date="minDate" :max-date="maxDate" @update:modelValue="onEndDate"  :disabled="!stay.can_change_end_date"  dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="text-center px-2 w-5rem">
                                <InputNumber v-model="stay.room_nights" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :max="maxNight" :min="1" class="child-adults-txt w-full" />
                            </td>
                            <td class="px-2"> 
                                <Dropdown :disabled="stay.room_id" v-model="stay.room_type_id" :options="room_types" optionValue="name"
                                     optionLabel="room_type" :placeholder="$t('Select Room Type')"
                                    class="w-full">
                                    <template #option="slotProps">
                                        <div class="flex align-items-center">

                                            <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room ||
                                                0 }})</div>
                                        </div>
                                    </template>
                                </Dropdown>

                               
                            </td>
                            <td class="ps-2">
                                <span class="p-inputtext-pt text-start border-1 border-white h-12 lg:w-full flex w-10rem">
                                    <span v-if="stay.room_number">{{ stay.room_number }}</span>
                                    <span v-else class="text-red-400">{{ $t('Unassign') }}</span>
                                </span>
                            </td> 
                        </tr>
                    </tbody>
                    <tbody>
                        <tr>
                            <td colspan="5">
                                <div class="text-right pt-2">
                                                            
                                    <div class="flex justify-end gap-3 mt-3">
                                        <div class="flex align-items-center">
                                            <RadioButton v-model="stay.generate_rate_type" inputId="regenerate_using_last_rate" name="regenerate" value="stay_rate" />
                                            <label for="regenerate_using_last_rate" class="ml-2 cursor-pointer">{{ $t('Generate New Stay Rate from First/Last Stay Rate') }}</label>
                                        </div>
                                        <div class="flex align-items-center">
                                            <RadioButton v-model="stay.generate_rate_type" inputId="regenerate_rate_use_rate_plan" name="regenerate" value="rate_plan" />
                                            <label for="regenerate_rate_use_rate_plan" class="ml-2 cursor-pointer">{{ $t('Generate New Stay Rate using Rate Plan') }}</label>
                                        </div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </template>
        </ComReservationStayPanel>
    </div>
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,postApi, computed} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import Enumerable from 'linq'
    import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const loading = ref(false) 
    const generate_new_room_rate = ref(true) 
    const maxNight = ref(null) 
    const stay = ref(JSON.parse(JSON.stringify(dialogRef.value.data.item)))
    stay.value.start_date = moment(stay.value.start_date).toDate()
    stay.value.end_date = moment(stay.value.end_date).toDate()
    stay.value.generate_rate_type  = "stay_rate"
    const stays = Enumerable.from(rs.reservationStay.stays).orderBy("$.start_date").toArray()
    const index = stays.findIndex(p => p.name == stay.value.name)
    const room_types = ref([])
    const minStartDate = computed(()=>{
        if(index > 0){
            const prevStay = stays[index - 1]
            return new Date(prevStay.end_date)
        }else{
            return new Date(working_day.date_working_day)
        }
    })
    const minDate = computed(()=>{
        if(moment(stay.value.start_date).isSame(working_day.date_working_day) || moment(stay.value.start_date).isBefore(working_day.date_working_day)){
            return new Date(moment(working_day.date_working_day).add(1,'days'))
        }else{
            return new Date(moment(stay.value.start_date).add(1,'days'))
        }
    })
    const maxDate = computed(()=>{
        if(stays[index + 1]){ 
            maxNight.value = moment(stays[index + 1].end_date).diff(moment(stay.value.start_date), 'days') - 1
            return moment(stays[index + 1].end_date).subtract(1, "days").toDate()
        }
        return null
    })
    
    function onStartDate(newValue){
        let end_date = moment(stay.value.end_date).format("YYYY-MM-DD")
        end_date = moment(end_date).toDate()

        if(moment(newValue).isSame(end_date) || moment(newValue).isAfter(end_date)){

            stay.value.end_date = moment(newValue).add(1,'days').toDate()
        }
        stay.value.room_nights = moment(stay.value.end_date).diff(moment(newValue), 'days') 
        getRoomType()
    }

    function onNight(newValue){
        stay.value.end_date = new Date(moment(stay.value.start_date).add(newValue,'days').toDate())
        getRoomType()
    }
    function onEndDate(newValue){
        stay.value.room_nights = moment(newValue).diff(moment(stay.value.start_date), 'days')
        getRoomType()

    }

    
const getRoomType = () => {

getApi("reservation.check_room_type_availability", {
    property: property.name,
    start_date: moment( stay.value.start_date).format("yyyy-MM-DD"),
    end_date: moment( stay.value.end_date).format("yyyy-MM-DD"),
    rate_type:  stay.value.rate_type,
    business_source: stay.value.business_source

})
    .then((result) => {
        room_types.value = result.message;
        
        
    })
}

    const onClose = () =>{
        dialogRef.value.close();
    }
    function onSave(){
        loading.value = true
        if(moment(stay.value.start_date).isSame(stay.value.end_date) || moment(stay.value.start_date).isAfter(stay.value.end_date)){
            gv.toast('warn','Departure date cannot less than or equal to arrival date.')
            loading.value = false
            return
        } 
        var newData = JSON.parse(JSON.stringify(stay.value))
        newData.start_date = gv.dateApiFormat(newData.start_date)
        newData.end_date = gv.dateApiFormat(newData.end_date)
        newData.rate = newData.input_rate
        newData.is_override_rate = generate_new_room_rate.value
        newData.is_move = 0
 
        
        postApi('reservation.change_stay', {data: newData}).then((r)=>{
            loading.value = false
            
            rs.getReservationDetail(rs.reservationStay.name)

            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"ReservationList"},"*")
         
            window.postMessage({action:"ReservationStayDetail"},"*")
          
            window.postMessage({action:"ReservationDetail"},"*")
          
            window.postMessage({"action":"Frontdesk"},"*")
            
            window.postMessage({action:"GuestLedger"},"*")
            window.postMessage({action:"GuestLedgerTransaction"},"*")
            
            
            onClose(true)
            
        }).catch(()=>{
            loading.value= false
        })
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: property.name
        }).then((result) => {
            working_day.value = (result.message)
            loading.value= false
            getRoomType();

        })
});
</script>
<style lang="">
    
</style>