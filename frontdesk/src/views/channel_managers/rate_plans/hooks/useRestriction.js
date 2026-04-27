import { ref } from "vue";

const restrictionData = ref({})
const restrictionTypeList = ref([])
export function useRestriction() {

    async function getRestrictionData(filter) {
        
        // filter={
        //     "restriction_type":"Stop Sale",
        //     "start_date","end_date","room_type":[]
        // }
        filter.property = window.property_name

        const res = await app.postApi("room_restriction.get_room_restriction_data",{
            filters: filter
        },
        "",
        false
    )

        if (res.data){
                Object.keys(res.data).forEach(key => {
                    restrictionData.value[key] = res.data[key]    
                })
                
          
        }

    }
    
  async function loadRestrictionTypeList() {
    try {
        const res = await app.postApi(
            "room_restriction.get_restriction_type_list",
            {
                property_name: window.property_name
            },"",
        false
        )
        restrictionTypeList.value = res?.data || []

    } catch (error) {
        console.error(error)
        restrictionTypeList.value = []
    }
     
}

    return {
        restrictionData,
        getRestrictionData,
        loadRestrictionTypeList,
        restrictionTypeList
    }


}