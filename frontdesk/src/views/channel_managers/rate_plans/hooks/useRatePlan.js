import { onMounted, inject, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
const roomTypes = ref([])
const selectedRoomTypes = ref([])
const selectRoomTypesData = ref([])
const initialized = ref(false)
const roomRatesData = ref([])
const rateType = ref("")
const startDate = ref() //get first day of year
const endDate = ref()
const years = ref([])
const selectedYear = ref(new Date().getFullYear())
const selectedDates = ref(new Set())
const occupancyCodes = ref([])
const hidePreviouseMonths = ref(false)


export function useRatePlan() {

    const route = useRoute();
    const moment = inject('$moment')
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const settingMenues = computed(() => [
        {
            label: hidePreviouseMonths.value
                ? "Show Previous Months"
                : "Hide Previous Months",
           icon: 'pi pi-calendar',
            command: async () => {
               await onTooglePreviouseMonth()
            }
        },
            {
        separator: true
    },
 {
            label:"View rate by Room Type", 
           icon:"pi pi-arrow-right-arrow-left",
            command: async () => {
               await onTooglePreviouseMonth()
            }
        },
    ])


    async function onTooglePreviouseMonth(){
         hidePreviouseMonths.value =
                    !hidePreviouseMonths.value

                localStorage.setItem(
                    "rate_plan_hide_previouse_months",
                    hidePreviouseMonths.value
                )

                if (hidePreviouseMonths.value) {
                    startDate.value = moment().startOf("month")
                } else {
                    startDate.value = moment().startOf("year")
                }

                await reloadRoomRatesData()
    }

    async function getRatePlanInfo() {
        const res = await app.getApi("rate_plan.get_rate_plan_info", {
            property: property.name,
            rate_type: rateType.value
        })

        if (res.data) {
            roomTypes.value = res.data.room_types
            if (roomTypes.value) {
                roomTypes.value[0].selected = true

            }
            years.value = res.data.visible_years
            occupancyCodes.value = res.data.occupancy_codes

            console.log(roomTypes.value)
        }
    }

    async function onSelectRoomType(room_types) {

        selectRoomTypesData.value =
            roomTypes.value.filter(x =>
                room_types.includes(x.edoor_room_type)
            )

        // await getRoomRateData(room_types)
    }



    async function getRoomRateData(filters) {

        console.log("filter=>", filters)
        const res = await app.postApi("rate_plan.get_room_rate_data", {
            filters: filters
        }, "", false)
        if (res.data) {
            roomRatesData.value = res.data
        }
    }

    function getSelectedRoomTypesID() {
        const _room_type_ids = roomTypes.value.filter(x => x.selected).map(r => r.edoor_room_type)
        if (_room_type_ids) return _room_type_ids
        return []
    }

    async function reloadRoomRatesData() {

        const l = await window.showLoading("Loading room rate data...")
        await getRoomRateData({
            room_types: getSelectedRoomTypesID(),
            rate_type: rateType.value,
            start_date: moment(startDate.value).format('YYYY-MM-DD'),
            end_date: moment(endDate.value).format('YYYY-MM-DD'),
        })
        l.close();

    }
    onMounted(async () => {

        // prevent multiple API calls
        if (initialized.value) return
        initialized.value = true

        // get state hide previouse month from localstorage 
        hidePreviouseMonths.value = (localStorage.getItem("rate_plan_hide_previouse_months") === "true")
        if (hidePreviouseMonths.value) {
            startDate.value = moment().startOf('month')

        } else {
            startDate.value = moment().startOf('year') //get first day of year
        }

        endDate.value = moment().endOf('year')

        rateType.value = route.params.name;

        const l = await window.showLoading()

        await getRatePlanInfo()
        await getRoomRateData({
            room_types: getSelectedRoomTypesID(),
            rate_type: rateType.value,
            start_date: moment(startDate.value).format('YYYY-MM-DD'),
            end_date: moment(endDate.value).format('YYYY-MM-DD'),
        })

        l.close()

    })

    function resetData() {

        roomTypes.value = []
        selectedRoomTypes.value = []
        selectRoomTypesData.value = []
        initialized.value = false
        roomRatesData.value = []
        rateType.value = ""
        years.value = []
        selectedYear.value = new Date().getFullYear()
        selectedDates.value = new Set();
        occupancyCodes.value = []

    }
    return {
        roomTypes,
        selectedRoomTypes,
        selectRoomTypesData,
        roomRatesData,
        years,
        selectedYear,
        rateType,
        startDate,
        endDate,
        selectedDates,
        occupancyCodes,
        settingMenues,
        onSelectRoomType,
        getRoomRateData,
        reloadRoomRatesData,
        resetData
    }
}