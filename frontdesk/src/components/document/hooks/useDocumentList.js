
import {onUnmounted, onMounted, ref,getDocumentList,postData,watch ,useRoute,getDocument,deleteDocument } from "@/plugin";
import { useApp } from "@/hooks/useApp";
import moment from "@/utils/moment.js";
import ComSaveView from  "@/components/document/components/ComSaveView.vue"
import ComListViewSetting from  "@/components/document/components/ComListViewSetting.vue"
import {i18n} from '@/i18n';
 
const { t: $t } = i18n.global; 
export   function useDocumentList(props,emit,dialog=null) {
    const route = useRoute();
    const options = props.options;
    const {getMeta,getListViewSetting} = useApp();
    const items = ref([])
    const loading = ref(true)
    const scrollHeight = ref()
    const filter = ref()
    const tempFilter = ref({keyword:""})

    const filters = ref([])
    const orFilters = ref([])
    const fields = ref(["name"])
    const meta =ref()
    const columns = ref([])
    const filterOptions = ref([])
    const orderBy = ref()
    const totalRecord = ref(0)
    const limit = ref(50)
    const viewList = ref([])
    const currentView=ref()
    const  saveViewList= ref(null); //we use to reload save view list via define expost when add or update view
    const listViewSetting = ref({})
 
    const contextMenuOptions = ref([
        // {label: 'View', icon: 'pi pi-fw pi-search', command: () =>alert(selectedRow.value.name)},
        // {label: 'Delete', icon: 'pi pi-fw pi-times', command: () =>alert(selectedRow.value.name)}
    ]);
    

const settingMenus = ref([
    
            {
                label: 'Save this view',
                icon: 'pi pi-plus',
                command: () => {
                    onCreateNewView()
                }
            },
            {
                label: 'View Setting',
                icon: 'pi pi-cog',
                command: ()=>{
                    onOpenListViewSetting();
                }
            },
            {
                label: 'Reset View',
                icon: 'pi pi-cog',
                command: ()=>{
                    deleteDocument("App List View Setting",props.list_view_setting,{
                        hide_error_message:true
                    })

                }
            },
            

]);

watch(() => route.hash, async (newHash) => {
    const view = viewList.value.find(r=>r.name == newHash.replace("#",""))
    if(view){
        
        filter.value = JSON.parse(view.custom_view_filters);//assign to this is use for generate filter send to db
        tempFilter.value  = JSON.parse(view.custom_view_filters);//assign to this is use in default filter selection
        
        currentView.value = view;
         
        await getData()
    }else {
        currentView.value = null
    }

  });
  

 
    function getOptions(){
     
      return  {
            fields : getFields().map(x=>x.fieldname),
            filters :  getFilters(),
            orFilters :  getOrFilters(),
            orderBy :   orderBy.value,
            limit:limit.value
        }
    }

    
    function getFields(){
        fields.value = []
        if(listViewSetting.value){
            fields.value =listViewSetting.value.fields
        }else {
            if(options.fields){
                fields.value =options.fields
            }else {
     
                fields.value = meta.value.fields.filter(r=>r.in_list_view==1 && r.fieldname).map(x=> {return {fieldname:x.fieldname}})
               
            }
        }
        
      

        return fields.value
      
      
    }

    async function getData(){
        loading.value = true ;
        const res = await getDocumentList(props.doctype,getOptions())
        if(!res.error){
            items.value = res.data;
        }
        loading.value = false

        // let get count run dependence no waiting to get data
        getCount();

       

    }

    async function getCount(){
        const res = await getDocumentList(props.doctype,{
            fields:["count(name) as total"],
            filters:filters.value,
            orFilters: orFilters.value
            
        },"",true,"") 
        if(!res.error){
            totalRecord.value = res.data[0].total
        }
        
    }

    function getFilters(){
        filters.value = []
        if (options.filters){
            filters.value = JSON.parse(JSON.stringify(options.filters)) 
        }
        
        
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

        filters.value.filter(x=>x[2]=='current_working_date').forEach(f=>{
            f[2] = moment(window.current_working_date).format("YYYY-MM-DD")
        })
       
        return filters.value

    }

    function getOrFilters(){
        orFilters.value = options.orFilters || []
        let searchFields = ["name"]
        if(props.searchFields){
            searchFields =   searchFields.concat(props.searchFields.split(","));
        }
 
        if(meta.value.search_fields){
           
           searchFields =  searchFields.concat(meta.value.search_fields.split(","));
        }

        

        if(filter.value?.keyword){
            searchFields.forEach(f=>{
                orFilters.value.push([f.trim(),'like','%' + filter.value.keyword + '%'])
            })
            
        }
        return orFilters.value;
        
    }

    

    async function onSearch(f){
        
        filter.value =JSON.parse(JSON.stringify(f)); 
       

        await getData();
    }

    function getColumns(){
        columns.value = [];

        fields.value.filter(x=>!x.is_hide).forEach((f)=>{
          
            // doclist query field can be assign alias field
            // so we use split with as keyword to get actual field and alias field
            // when field label will be use alias
            const arrField = f.fieldname.split("as")
            const field = meta.value.fields.find(r=>r.fieldname == arrField[0].trim())
            if (field){
                columns.value.push({
                    field:arrField.length==1?field.fieldname:arrField[1].trim(),
                    header: f.label || field.label,
                    fieldtype:f.fieldtype ||  field.fieldtype,
                    header_class: getAlignmentClass(field)
                })
            }else if (["name","owner","modified",'creation','modified_by'].includes(f.fieldname)){
                
                columns.value.push({
                    field:f.fieldname,
                    header: f.label || f.fieldname,
                    fieldtype:f.fieldtype ,
                    header_class: getAlignmentClass(f)
                })
            }
        })
       
       
        return columns.value;
       
    }



    function getAlignmentClass(f){
        if (['Int','Float','Date','Decimal'].includes(f.fieldtype)){
            return 'text-center'
        }else if (['Currency'].includes(f.fieldtype)){
            return 'text-right'
        }
        return 'text-left'
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

    async function onOrderBy(data){
       
        orderBy.value = {
            field: data.order_by,
            order: data.order_type
    }
    await getData();
    }

    function onCreateNewView(){
         const dialogRef = dialog.open(ComSaveView, {
            data: {
                doctype: props.doctype,
                view_filters:tempFilter.value,
                filters:filters.value,
                current_view:currentView.value
            },
            props: {
                header: $t("Save View") ,
                style: {
                    width: '35vw',
                },
                position:"top",
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                breakpoints:{
                    '960px': '50vw',
                    '640px': '100vw'
                },
            },
            onClose: (options) => {
                if(options.data){
                    saveViewList.value.reloadData();
                }
            }
           
        });
    }

    
    function onOpenListViewSetting(){
       let listSetting = {}
       if(listViewSetting.value){
            listSetting = {
                name:  listViewSetting.value.name,
                filter_options:  listViewSetting.value.filter_options,
                fields:  listViewSetting.value.fields
            }
       }else {
        listSetting.name = props.list_view_setting
        
        listSetting.filter_options = filterOptions.value
        listSetting.fields = getFields();

       }

        const dialogRef = dialog.open(ComListViewSetting, {
           data: {
                doctype:props.doctype,
               ...listSetting
           },
           props: {
               header: $t("List View Setting") ,
               style: {
                   width: '80vw',
               },
               position:"top",
               modal: true,
               maximizable: true,
               closeOnEscape: false,
               breakpoints:{
                   '960px': '50vw',
                   '640px': '100vw'
               },
           },
           onClose: async (options) => {
               if(options.data){
                 window.location.reload();
               }
           }
          
       });
   }

    async function onLimitChanged (){
        await getData()
    }

    async function getFilterSetting(){
        const res = await getDocument("List Filter",window.location.hash.replace("#",""))
        if(res.data){
            filter.value = JSON.parse(res.data.custom_view_filters)
            tempFilter.value = filter.value//we use this to set default selected to filter option
            currentView.value = res.data
        }
    }

    function getFilterOptions(){
        filterOptions.value = options.filterOptions || []
        
        if (!filterOptions.value || filterOptions.value.length==0){
            filterOptions.value = meta.value.fields.filter(x=>x.in_standard_filter ==1)
        }else {
            // user send fitler option by prop get extra meta data field
            // like field type, link option... label ...
            filterOptions.value.forEach(f=>{
                const metaField = meta.value.fields.find(x=>x.fieldname == f.fieldname);
              
                f.fieldtype = f.fieldtype || metaField.fieldtype
                f.label= f.label || metaField.label
                f.options= f.options || metaField.options
            })
         
        }
     return filterOptions.value;
    }


    function onRowDoubleClick(event){
        
        emit("row-dblclick",event.data)
    }

     
    const actionRefreshData = async function (e) {
     
        if (e.isTrusted && typeof (e.data) != 'string') {
            if (e.data.action == "ComDocumentList") {

               getData();
            }
        };
    }
    

    onMounted(async ()=>{
        scrollHeight.value = getScrollHeight();
        meta.value =  await getMeta(props.doctype)
        listViewSetting.value = await getListViewSetting(props.list_view_setting)
      
        if(window.location.hash){
            await getFilterSetting()
        }
        await getData();
        getColumns();

        orderBy.value =  {
                field: meta.value.sort_field,
                order: meta.value.sort_order
        }

        getFilterOptions()
 

        // append setting menu
        if(options.settingMenus){
        
            settingMenus.value = settingMenus.value.concat(options.settingMenus)
        }

        if (options.limit){
            limit = props.limit
        }

 
        window.addEventListener('message', actionRefreshData, false);
        
    })

    onUnmounted(()=>{
        window.removeEventListener('message', actionRefreshData, false);
    })

    
  return { 
    loading,
    fields,
   items,
   scrollHeight,
   columns,
   filterOptions,
   settingMenus,
   tempFilter,
   totalRecord,
   limit,
   viewList,
   currentView,
   saveViewList,
   contextMenuOptions,
   onLimitChanged,
   onLoadMore,
   onSearch,
   onOrderBy,
   onRowDoubleClick,
   getData
   
};
}
