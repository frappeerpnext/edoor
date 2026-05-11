import { onMounted, inject, ref } from 'vue'

// state variable
const data = ref([])
const roomTypes = ref([])
const selectedData = ref([])

const filters = ref({})
const isInitialize = ref(false)

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


    async function getData(start_date, end_date) {
        const res = await app.getApi("room_availability.get_room_availability", {
            property:window.property_name,
            start_date: moment.utc(start_date).format("YYYY-MM-DD"),
            end_date: moment.utc(end_date).format("YYYY-MM-DD")
        })
        if (res.data) {
            data.value = res.data
        }
    }


    async function onRefresh() {
        const l = await window.showLoading();
        await getRoomTypes()
        await getData(filters.value.start_date, filters.value.end_date);
        l.close()
    }


    async function updateAvailabiltyRestricion(status) {


        const l = await window.showLoading()
        // alert(123555)

        const res = await app.postApi("room_availability.update_room_availability_restriction", {
            property: window.property_name,
            stop_sale: status,
            data: selectedData.value.map(x => {
                return {
                    room_type: x.room_type,
                    date: x.date
                }
            })
        })

        if (res.data) {
            await getData(filters.value.start_date, filters.value.end_date);
            refAvailability.value.clearSelections()
        }

        l.close();
    }

    async function toggleUpdateAvailabilityRestriction(room_type, date, status) {


       

        const updatedData = data.value.find(r => r.room_type_id == room_type && r.date == date);
        if (updatedData) {
            updatedData.loading = true
        }

        const res = await app.postApi("room_availability.toggle_update_availability_restriction", {
            data: {
                property: window.property_name,
                stop_sale: status,
                room_type_id: room_type,
                date: date


            }


        })

        if (res.data) {
            const updatedData = data.value.find(r => r.room_type_id == room_type && r.date == date);
            if (updatedData) {
                updatedData.stop_sale = status
                updatedData.loading = false
            }

            refAvailability.value.clearSelections()
        }
        
    }

    onMounted(async () => {
        if(!isInitialize) return
        isInitialize.value = true;

        filters.value = {
            start_date: moment().toDate(),
            end_date: moment().add(1, "year").toDate()
        }
        filters.value.dates = [ "dates", "Between", [  moment().toDate(),  moment().add(1, "year").toDate() ] ]
       
        await getRoomTypes()
        await getData(filters.value.start_date, filters.value.end_date);
    })


    return {
        roomTypes,
        data,
        filters,
        refAvailability,
        selectedData,
        getData,
        onRefresh,
        updateAvailabiltyRestricion,
        toggleUpdateAvailabilityRestriction

    }
}