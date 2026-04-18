<template>
 <ComDialogContent  hideButtonClose titleButtonOK="Ok" :hideIcon="false" :hideButtonOK="true">
  
    <div class="flex flex-column gap-4">

      <!-- STATUS HEADER -->
      <div class="flex align-items-center justify-content-between">

        <div class="flex align-items-center gap-2">
          <Tag
            :severity="statusSeverity"
            :value="log?.status"
            class="text-lg"
          />

          <span class="text-xl font-bold">
            {{ log?.title }}
          </span>
        </div>

        <span class="text-500 text-sm">
          {{log?.title}} at {{moment(log?.creation).format("DD-MM-YYYY hh:mm A")}}
        </span>

      </div>

      <!-- SUMMARY INFO -->
      <Card>
        <template #content>

          <div class="grid">

            <div class="col-6 md:col-3">
              <div class="text-500 text-sm">Provider</div>
              <div class="font-medium">
                {{ log?.provider }}
              </div>
            </div>

            <div class="col-6 md:col-3">
              <div class="text-500 text-sm">Property</div>
              <div class="font-medium">
                {{ log?.property }}
              </div>
            </div>

            <div class="col-6 md:col-3">
              <div class="text-500 text-sm">Sync Action</div>
              <Tag severity="danger">
                {{ log?.sync_action }}
              </Tag>
            </div>

            <div class="col-6 md:col-3" v-if="log?.title == 'Delay Sync'">
              <div class="text-500 text-sm">Delay until</div>
              <div class="font-medium">
              {{moment(log?.sync_until).format("DD-MM-YYYY hh:mm A")}}  
              </div>
            </div>

 
          </div>

        </template>
      </Card>

      <!-- ERROR MESSAGE -->
      <Message
        severity="warn"
        icon="pi pi-exclamation-triangle"
      >
        <div class="font-medium mb-2">
          Channel Manager Response
        </div>

        <div class="font-mono text-sm">
          {{ log?.response_text }}
        </div>

      </Message>
 
      <!-- RATES TABLE -->
      <Card
         v-if="log?.title == 'Prices update'"
      >

        <template #title>
          Rates Detail
        </template>

        <template #content>

          <DataTable
            :value="log?.data"
            stripedRows
            responsiveLayout="scroll"
           
          >

            

            <Column
              field="room_type"
              header="Room Type"
            />

            <Column
              field="period"
              header="Periods"
            >
              <template #body="slotProps">

                <span class="font-medium">
                    <div v-for="d in slotProps.data.period">
                        {{ moment(d.start_date).format("DD-MM-YYYY") }} to {{ moment(d.end_date).format("DD-MM-YYYY") }}
                    </div>
                  
                </span>

              </template>
            </Column>
            <Column
              field="rate"
              header="Rate"
            >
              <template #body="slotProps">

                <span class="font-medium">
                    <div v-for="r in slotProps.data.rates">
                        
                      <CurrencyFormat :value="r.rate"></CurrencyFormat> /  {{ r.title }}
                    </div>
                  
                </span>

              </template>
            </Column>

          </DataTable>

        </template>
      </Card>

     

    </div>
 
    <template #footer-right >
      
      <Button label="Retry Sync" v-if="log?.sync_action== 'Stop Sync' && log?.is_retry_sync == 0"  icon="pi pi-sync" @click="onRetrySync"/>
    </template>
 </ComDialogContent>
</template>
<script setup>
import { onMounted, ref,inject,computed } from 'vue';

import Tag from 'primevue/tag';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
const moment = inject("$moment")
    const dialogRef = inject("dialogRef");
    const log = ref()

    const statusSeverity = computed(() => {

        if (log.value?.status === "Success")
            return "success";

        if (log.value?.status === "Warning")
            return "warning";

        if (log.value?.status === "Error")
            return "danger";

        return "info";

        });


    async function getLog(){
        
        const res = await app.getApi("edoor.channel_managers.utils.get_cm_sync_log_data",{
            docname:dialogRef.value.data.docname
        })
        if (res.data){
            log.value = res.data
        }
       

    }

    function onRetrySync(){
      dialogRef.value.close({retry_sync:true})
    }
    onMounted(async ()=>{
        
        await getLog()    
        
        
    })
</script>