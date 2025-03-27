
import { onMounted, ref,getDocumentList } from "@/plugin";
import { useApp } from "@/hooks/useApp";

export   function useDocumentList(props) {
    const {getMeta} = useApp();
    const items = ref([])
    const loading = ref(true)
    const scrollHeight = ref()
    const filter = ref()
    const filters = ref([])
    const orFilters = ref([])
    const fields = ref(["name"])
    const meta =ref()
    const columns = ref([])
    const filterOptions = ref([])


    function getOptions(){
        let options = props.options
        options.fields = getFields();
        options.filters =  getFilters()
        options.orFilters =  getOrFilters()
        // options.orderBy =   {
        //     field: 'reservation',
        //     order: 'asc',
        //   }

        return  options
    }

    function getFields(){
       
        if(props.fields){
            fields.value =filters.value.concat(props.fields)
        }else {
          
 
            fields.value = fields.value.concat(meta.value.fields.filter(r=>r.in_list_view==1).map(x=>x.fieldname))
           
        }
        
        if(props.extraFields){
            return  [...new Set(fields.value.concat(props.extraFields ))];
        }else {
            return  [...new Set(fields.value)];
        }
       

      
    }

    async function getData(){
        loading.value = true ;
        const res = await getDocumentList(props.doctype,getOptions())
        if(!res.error){
            items.value = res.data;
        }
        loading.value = false
    }

    function getFilters(){
        filters.value = props.filters || []
        
        if(filter.value){
            Object.keys(filter.value).forEach(key => {
                if(key!='keyword'){
                  
                    if((typeof filter.value[key][0]) == 'string'){
                        filters.value.push(filter.value[key])
                    }else {
                        
                        filters.value = filters.value.concat(filter.value[key])
                    }
                    
                }
              });
        }
        
        return filters.value

    }
    function getOrFilters(){
        orFilters.value = props.orFilters || []
        let searchFields = ["name"]
        if(props.searchFields){
            searchFields =   searchFields.concat(props.searchFields.split(","));
        }
 
        if(meta.value.search_fields){
           
           searchFields =  searchFields.concat(meta.value.search_fields.split(","));
        }

        

        if(filter.value?.keyword){
            searchFields.forEach(f=>{
                orFilters.value.push([f.trim(),'like','%' + encodeURIComponent(filter.value.keyword) + '%'])
            })
            
        }
        return orFilters.value;
        
    }

    async function onSearch(f){
        console.log(f)
        filter.value = f;
  
        await getData();
    }

    function getColumns(){
        const displayFields = meta.value.fields.filter(x=>fields.value.includes(x.fieldname))
        displayFields.forEach(f=>{
            columns.value.push({
                field:f.fieldname,
                header:f.label
            })
        })
        
        
    }

    function onLoadMore(){
      
    }

    function getScrollHeight(){
      
        const myDiv = document.getElementById('table-container');
        let h = window.innerHeight;
        myDiv.style.height = `${h}px`;
        while ( document.body.scrollHeight > document.body.clientHeight){
            h = h-10;
            myDiv.style.height = `${h}px`;
           
            
        }
        
        return `${h}px`;

    }


    onMounted(async ()=>{
        scrollHeight.value = getScrollHeight();
        meta.value =  await getMeta(props.doctype)
        await getData();
        getColumns();



        filterOptions.value = props.filterOptions || []

        if (!filterOptions.value || filterOptions.value.length==0){
            filterOptions.value = meta.value.fields.filter(x=>x.in_standard_filter ==1)
        }
        
    })

    
  return { 
    loading,
    fields,
   items,
   scrollHeight,
   columns,
   filterOptions,
   onLoadMore,
   onSearch,
   
};
}
