import { onMounted, inject, ref, computed } from 'vue'
import ComRatePlanInfo from "@/views/channel_managers/rate_plans/components/ComRatePlanInfo.vue"
import ComRoomRate from "@/views/channel_managers/rate_plans/components/ComRoomRate.vue"
import ComRestriction from "@/views/channel_managers/rate_plans/components/ComRestriction.vue"
import ComCMSyncLog from "@/views/channel_managers/rate_plans/components/ComCMSyncLog.vue"
import ComChangeDataLog from "@/views/channel_managers/rate_plans/components/ComChangeDataLog.vue"
import { useRestriction } from '@/views/channel_managers/rate_plans/hooks/useRestriction'
import { useRoute } from 'vue-router'
const ratePlan = ref({})
const roomTypes = ref([])
const rateInfo = ref({})
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
const ratePlanMappedList = ref([])
const prodiverName = ref('')
const cmRestrictions = ref([])
const restrictionTypesOption = ref([])
const defaultFilterRestriction = ref([])

const cm_info = ref()

const components = ref([
    { component:"ComRatePlanInfo",is_loaded: true,title:"Rate Plan Information"},
    { component:"ComRoomRate",is_loaded: false,title:"Room Rate"},
    { component:"ComRestriction",is_loaded: false,title:"Restriction"},
    
    { component:"ComChangeDataLog",is_loaded: false,title:"Change Data Log"}
])

const componentsMap = {
    "ComRatePlanInfo":ComRatePlanInfo,
    "ComRoomRate":ComRoomRate,
    "ComRestriction":ComRestriction,
    "ComCMSyncLog":ComCMSyncLog,
    "ComChangeDataLog":ComChangeDataLog
}

const savedselectedRestrictionTypes = localStorage.getItem("selectedRestrictionTypes")

const selectedRestrictionTypes = ref([]
//   savedselectedRestrictionTypes ? JSON.parse(savedselectedRestrictionTypes) : defaultFilterRestriction.value
)
const restrictionTypes = [
    {
    restriction_type: "Closed",
    lower_char: "closed",
    default_value: 1,
    show_radio_input: true,
    show_number_input: false,
    show_reset_value: false,
    },
    {
    restriction_type: "Cta",
    lower_char: "cta",
    default_value: 1,
    show_radio_input: true,
    show_number_input: false,
    show_reset_value: false,
    },
    {
    restriction_type: "Ctd",
    lower_char: "ctd",
    default_value: 1,
    show_radio_input: true,
    show_number_input: false,
    show_reset_value: false,
    },
    {
    restriction_type: "MinLos",
    lower_char: "minlos",
    default_value: 0,
    show_radio_input: false,
    show_number_input: true,
    show_reset_value: true,
    },
    {
    restriction_type: "MaxLos",
    lower_char: "maxlos",
    default_value: 0,
    show_radio_input: false,
    show_number_input: true,
    show_reset_value: true,
    },
    {
    restriction_type: "MinLosArrival",
    lower_char: "minlosarrival",
    default_value: 0,
    show_radio_input: false,
    show_number_input: true,
    show_reset_value: true,
    },
    {
    restriction_type: "MaxLosArrival",
    lower_char: "maxlosarrival",
    default_value: 0,
    show_radio_input: false,
    show_number_input: true,
    show_reset_value: true,
    },
    {
    restriction_type: "MinAdvBooking",
    lower_char: "minadvbooking",
    default_value: 0,
    show_radio_input: false,
    show_number_input: true,
    show_reset_value: true,
    },
    {
    restriction_type: "MaxAdvBooking",
    lower_char: "maxadvbooking",
    default_value: 0,
    show_radio_input: false,
    show_number_input: true,
    show_reset_value: true,
    },
    {
    restriction_type: "FullPatternLos",
    lower_char: "fullpatternlos",
    default_value: 0,
    show_radio_input: false,
    show_number_input: false,
    show_reset_value: false,
    show_date_selection: true,
    }
]

const selectedComponent = ref("ComRatePlanInfo")

export function useRatePlan() {

    
    const route = useRoute();
    const moment = inject('$moment')
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const {
        getRestrictionData,
        restrictionData
    } = useRestriction()

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
            label: "View rate by Room Type",
            icon: "pi pi-arrow-right-arrow-left",
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
                // xxx
    }

    async function getCMRestrictions() {
      
        const res = await app.getApi("rate_plan.get_restriction_codes", {property: property.name,rate_type:rateType.value})
        if (res.data) {
            cmRestrictions.value = Object.entries(res.data).filter(([key, value]) => value != 0).map(([key, value]) => ({key,value}))}
            const keys = cmRestrictions.value.map(x => x.key)

            restrictionTypesOption.value = restrictionTypes.filter(x => keys.includes(x.lower_char)) 

            defaultFilterRestriction.value = restrictionTypesOption.value.slice(0, 3).map(x => x.restriction_type)
    }


    async function getRatePlanInfo() {
        const res = await app.getApi("rate_plan.get_rate_plan_info", {
            property: property.name,
            rate_type: rateType.value
        })

        if (res.data) {

            ratePlan.value = res.data;
            ratePlanMappedList.value = res.data.cm_rate_plan_list
            rateInfo.value = {  
                "rate_type": res.data.rate_type, 
                "cm_rate_plan_list": ratePlanMappedList.value.find(r => r.edoor_rate_plan === res.data.rate_type.name) || {},
                "room_rate_min_max_date": res.data.room_rates_min_max_date.find(r => r.rate_type === res.data.rate_type.name) 
            };
            if (ratePlanMappedList.value.find(r => r.edoor_rate_plan === res.data.rate_type.name) != undefined) {
                prodiverName.value = res.data.cm_info.provider 
            }
            roomTypes.value = res.data.room_types 
            if (roomTypes.value && roomTypes.value.length > 0) {
                roomTypes.value[0].selected = true

            }
            years.value = res.data.visible_years
            occupancyCodes.value = res.data.occupancy_codes
            cm_info.value = res.data.cm_info
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
        const filter = {
            room_types: getSelectedRoomTypesID(),
            rate_type: rateType.value,
            start_date: moment(startDate.value).format('YYYY-MM-DD'),
            end_date: moment(endDate.value).format('YYYY-MM-DD'),
        }
        await getRoomRateData(filter)
        // get stop sale data   

        await getRestrictionData({
            "restriction_types":["Closed"],
            ...filter
        })


         
        l.close();

    }

    async function reloadRestrictionData(restriction_type) {

         const l = await window.showLoading("Loading restriction data...")
        const filter = {
            room_types: getSelectedRoomTypesID(),
            rate_type: rateType.value,
            start_date: moment(startDate.value).format('YYYY-MM-DD'),
            end_date: moment(endDate.value).format('YYYY-MM-DD'),
        }
        
        let _restrictionTypes = []
        if (restriction_type){
            if ((typeof restriction_type) == "string"){
                
                _restrictionTypes = [restriction_type]
            }else {
                _restrictionTypes = restriction_type
            }
            
        }else 
        {
            _restrictionTypes = selectedRestrictionTypes.value
        }
        await getRestrictionData({
            "restriction_types":_restrictionTypes,
            ...filter
        })

        l.close()
         
      

    }

    


    async function onRefresh() {
        if (selectedComponent.value =="ComRoomRate"){
             
            await reloadRoomRatesData()
            
        }else  if (selectedComponent.value == "ComRestriction"){
            
            await reloadRestrictionData();
        }
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
        await getCMRestrictions()
        // hide cm sync log if not have cm integration
        if(prodiverName.value && rateInfo.value?.cm_rate_plan_list?.cm_rate_plan){
            if (!components.value.find(x=>x.component == "ComCMSyncLog")){
                components.value.splice(3, 0, { component:"ComCMSyncLog",is_loaded: false,title:"Channel Manager Sync Log"});
            }
        }else {
            if (components.value.find(x=>x.component == "ComCMSyncLog")){
                components.value.splice(3, 1);
            }
        }

        selectedRestrictionTypes.value = savedselectedRestrictionTypes ? JSON.parse(savedselectedRestrictionTypes) : defaultFilterRestriction.value

       

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
        cmRestrictions.value = []
        restrictionTypesOption.value = []
        
        components.value.forEach(x=>x.is_loaded=false)
        selectedComponent.value = "ComRatePlanInfo"


    }
    return {
        property,
        ratePlan,
        rateInfo,
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
        components,
        selectedComponent,
        componentsMap,
        cm_info,
        restrictionData,
        prodiverName,
        restrictionTypes,
        selectedRestrictionTypes,
        cmRestrictions,
        restrictionTypesOption,
        onSelectRoomType,
        getRoomRateData,
        reloadRoomRatesData,
        resetData,
        onRefresh,
        reloadRestrictionData,
        getCMRestrictions
    }
}