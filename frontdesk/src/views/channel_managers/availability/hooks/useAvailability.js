import { onMounted, inject, ref } from 'vue'

// state variable
const data = ref([])
const roomTypes = ref([])
 
const filters = ref({})
const isInitialize = ref(false)
const closeRestrictionData = ref()
const oldFitlers = ref({})
export function useAvailability() {
    const moment = inject('$moment')
    
    const refAvailability = ref(null)


    // methods
    async function getRoomTypes() {

        const res = await app.getApi("utils.get_room_type_list",{
            property:window.property_name
        })

        if (res.data) {
            roomTypes.value = res.data  
        }

    }


    async function getData() {
        
        const start_date =moment.utc( filters.value.dates[2][0]).format("YYYY-MM-DD")
        const end_date=moment.utc( filters.value.dates[2][1]).format("YYYY-MM-DD")

        const res = await app.postApi("room_availability.get_room_availability", {
            property:window.property_name,
            start_date: moment.utc(start_date).format("YYYY-MM-DD"),
            end_date: moment.utc(end_date).format("YYYY-MM-DD"),
            room_types:filters.value.room_types?filters.value.room_types[2]:null
        },"",false)
        if (res.data) {
            data.value = res.data
        }
    }
    
    async function getCloseRestrictionData() {
        const start_date =moment.utc( filters.value.dates[2][0]).format("YYYY-MM-DD")
        const end_date=moment.utc( filters.value.dates[2][1]).format("YYYY-MM-DD")
 

        const res = await app.postApi("room_restriction.get_room_restriction_data", {filters:{ 
            property:window.property_name,
            restriction_types:["Closed"],
            start_date: moment.utc(start_date).format("YYYY-MM-DD"),
            end_date: moment.utc(end_date).format("YYYY-MM-DD"),
            room_types:filters.value.room_types?filters.value.room_types[2]:null,
            rate_type:filters.value.rate_type?filters.value.rate_type[2]:null
    }},"",false)
        if (res.data) {
            closeRestrictionData.value = res.data
        }
    }



    async function validateOccupancyData(){
        await app.postApi("schedule_task.fix_daily_property_data",null,"",false)
    }

    async function onRefresh() {
        
        const l = await window.showLoading();
        await validateOccupancyData()
        await getRoomTypes()
        await getData();
        await getCloseRestrictionData();
    l.close()
    }

    
    async function getDefaultRateType(){
         const res = await app.getDocList("Rate Type", { filters: { "property":window.property_name, is_default_rate_type: 1 } })
    if (res.data.length > 0) {
       
        filters.value.rate_type = ["rate_type", "=", res.data[0].name]
    }



    }
     
    onMounted(async () => {
   
        if(isInitialize.value) return
        isInitialize.value = true;
    
        filters.value.dates = [ "dates", "Between", [  moment().toDate(),  moment().add(1, "year").toDate() ] ]
        const l = await window.showLoading();
 
        await getRoomTypes()
        await getDefaultRateType()
        await getData();
        await getCloseRestrictionData()
      

            oldFitlers.value = JSON.parse(JSON.stringify(filters.value))
        l.close();
    })

    function resetData(){
        isInitialize.value = false
        data.value = {}
        closeRestrictionData.value = {}

    }


    return {
        roomTypes,
        data,
        filters,
        oldFitlers,
        refAvailability,
       resetData,
        closeRestrictionData,
        getData,
        onRefresh,
        getCloseRestrictionData
      
        

    }
}