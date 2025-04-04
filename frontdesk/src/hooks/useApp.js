
import { onMounted, ref,getData,getDocument } from "@/plugin";
 


const isCityLedgerInvoiceDetailOpen = ref(false)
const dialogBoxRef= ref()
const metas = ref([])
const listViewSettings = ref([])

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


  return { 
    isCityLedgerInvoiceDetailOpen,
    getMeta,
    getDoctypeDefaultFields,
    getListViewSetting
};
}
