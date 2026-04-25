
import { onMounted, ref,getData,getDocument } from "@/plugin";
 


const isCityLedgerInvoiceDetailOpen = ref(false)
const dialogBoxRef= ref()
const metas = ref([])
const listViewSettings = ref([])
const todaySummary =ref()

// channel manager info
const cmInfo = ref(null)





export function useApp() {



      async function getMeta(doctype){
      
        const existingDoctype = metas.value.find(r=>r.name == doctype);
      
        if(existingDoctype){
        
          return existingDoctype
        }
    
        const response =await getData("frontdesk.get_meta",{
          doctype:doctype
        });
        
        if(response.data){
          metas.value.push(response.data);
          return response.data;
        }
    
    
      }
     
      async function getListViewSetting(list_view_setting_name){
      
        const data = listViewSettings.value.find(r=>r.name == list_view_setting_name);
      
        if(data){
        
          return data
        }
    
        const res =await getDocument("App List View Setting",list_view_setting_name,false);
        
        if(res.data){
          res.data.fields =  JSON.parse(res.data.fields)
          res.data.filter_options=  JSON.parse(res.data.filter_options)
          listViewSettings.value.push(res.data);
          return res.data;
        }

        return null
    
    
      }




  async function getDoctypeDefaultFields(docType){
    let fields = ["name"]
    const meta = await getMeta(docType)
    if (meta.image_field) {
      fields.push(meta.image_field)
    }

    if (meta.title_field) {
      fields.push(meta.title_field)
    }
    
    if (meta.search_fields) {
      fields = [...fields, ...meta.search_fields.split(",").map((item) => item.trim())];
    }

    return [...new Set(fields)];

  }

  function onOpenLink(action, name) {
        
    window.postMessage(action + '|' + name, '*')
}

  async function getSummaryData(date){
    
  const res = await getData("frontdesk.get_dashboard_data",{
    property:window.property_name,
    date:date
  })
  if(res.data){
    
    todaySummary.value = res.data
  }
}

async function getCMInfo(){
  if (cmInfo.value) return cmInfo.value
  
  const res = await app.getApi("edoor.channel_managers.utils.get_channal_manager_info",{
    property:window.property_name
  })
  if(res.data){
    cmInfo.value = res.data
    return cmInfo.value
  }

}

  return { 
    isCityLedgerInvoiceDetailOpen,
    todaySummary,
    cmInfo,
    getCMInfo,
    getMeta,
    getDoctypeDefaultFields,
    getListViewSetting,
    onOpenLink,
    getSummaryData
};
}
