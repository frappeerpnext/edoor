
import { onMounted, ref,getData } from "@/plugin";
 


const isCityLedgerInvoiceDetailOpen = ref(false)


export function useApp() {

  const metas = ref([])

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
    getDoctypeDefaultFields
};
}
