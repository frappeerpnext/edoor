<template>
    <div>
   <div class="">
    <div class="max-w-7xl mx-auto">
      <!-- 3. Room Mapping Section -->
      <section id="sec-rooms" class="mb-5">
        <h2 class="text-xl font-semibold mb-3 flex align-items-center gap-2">
          <i class="pi pi-home text-primary"></i> Room Type Mapping
        </h2>
        <DataTable :value="channelManagerData.room_types" class="shadow-1 border-round overflow-hidden" responsiveLayout="scroll">
          <Column field="room_type_name" header="Room Type" style="width: 25%"></Column>
          <Column field="room_type_code" header="Provider Code"></Column>
          <Column field="edoor_room_type" header="eDoor Room Type ID">
            <template #body="sp">
              {{ sp.data.edoor_room_type }}
            </template>
          </Column>
        </DataTable>
      </section>

      <!-- 4. Rate Plans Section -->
 <!-- 4. Rate Plans Section -->
      <section id="sec-rates" class="mb-5">
        <h2 class="text-xl font-semibold mb-3 flex align-items-center gap-2">
          <i class="pi pi-money-bill text-primary"></i> Rate Plan Mapping
        </h2>
        
        <DataTable 
          :value="channelManagerData.rate_plans" 
          class="shadow-1 border-round overflow-hidden p-datatable-sm" 
          responsiveLayout="stack" 
          stripedRows
        >
          <Column field="rate_plan_name" :header="channelManagerData.provider + ' Rate Plan'" style="width: 30%"></Column>
          
          <Column field="rate_plan_code" header="Provider Code">
            <template #body="sp">
              <span class="font-mono text-700">{{ sp.data.rate_plan_code }}</span>
            </template>
          </Column>

          <Column field="edoor_rate_plan" header="eDoor Rate Plan">
            <template #body="sp">
              {{ sp.data.edoor_rate_plan }}
            </template>
          </Column>

          <Column field="availabilty_block_name" header="Availability Block">
            <template #body="sp">
              <div class="flex flex-column">
                <span class="text-sm">{{ sp.data.availabilty_block_name }}</span>
                <small class="text-400">ID: {{ sp.data.availability_block }}</small>
              </div>
            </template>
          </Column>
        </DataTable>
      </section>

      <!-- 5. Service Mapping Section -->
   <section id="sec-services" class="mb-5">
        <h2 class="text-xl font-semibold mb-3 flex align-items-center gap-2">
          <i class="pi pi-box text-primary"></i> Service Mapping
        </h2>
        
        <DataTable 
          :value="channelManagerData.services" 
          class="shadow-1 border-round overflow-hidden p-datatable-sm" 
          >
          <Column field="service_name" header="Service Name" style="width: 40%"></Column>
          
          <Column field="services_code" header="Provider Code">
            <template #body="sp">
              <span class="text-600 font-mono">{{ sp.data.services_code }}</span>
            </template>
          </Column>

          <Column field="edoor_service_code" header="eDoor Service Code" >
            <template #body="sp">
              <div class="flex align-items-center gap-2">
                {{ sp.data.edoor_service_code }}
              </div>
            </template>
          </Column>
        </DataTable>
      </section>

        <section id="sec-services" class="mb-5">
        <h2 class="text-xl font-semibold mb-3 flex align-items-center gap-2">
          <i class="pi pi-briefcase text-primary"></i> 

      Package Rule Mapping
        </h2>
        
   <DataTable 
  :value="channelManagerData.package_rule_mapping" 
  class="shadow-1 border-round overflow-hidden p-datatable-sm"
>
  <!-- The Empty State Template -->
  <template #empty>
    <div class="p-3 text-center text-500">
      No Data Found.
    </div>
  </template>

  <Column field="service_type" header="Service Type" style="width: 40%"></Column>
  
  <Column field="edoor_posting_rule" header="eDoor Posting Rule">
    <template #body="sp">
      <span class="text-600 font-mono">{{ sp.data.services_code }}</span>
    </template>
  </Column>

  <Column field="edoor_charge_rule" header="eDoor Charge Rule">
    <template #body="sp">
      <div class="flex align-items-center gap-2">
        {{ sp.data.edoor_charge_rule }}
      </div>
    </template>
  </Column>
</DataTable>
      </section>

      
        <section id="sec-services" class="mb-5">
        <h2 class="text-xl font-semibold mb-3 flex align-items-center gap-2">
          <i class="pi pi-folder text-primary"></i> 

      Business Source Mapping
        </h2>
        
   <DataTable 
  :value="channelManagerData.package_rule_mapping" 
  class="shadow-1 border-round overflow-hidden p-datatable-sm"
>
  <!-- The Empty State Template -->
  <template #empty>
    <div class="p-3 text-center text-500">
      No Data Found.
    </div>
  </template>

  <Column field="cm_business_source" header="CM Business Source" style="width: 40%"></Column>
  
  <Column field="edoor_business_source" header="eDoor Business Source">
    <template #body="sp">
      <span class="text-600 font-mono">{{ sp.data.edoor_business_source }}</span>
    </template>
  </Column>
</DataTable>
      </section>


    </div>
  </div>
        
      <!-- Footer -->
    <div class="footer flex gap-2">
  <Button 
    @click="onChangeDataUploadStep(-1)" 
    class="btn-back" 
    icon="pi pi-arrow-left"
    :label="$t('Back')"
  />

  <Button 
    @click="onChangeDataUploadStep(1)" 
    class="btn-next" 
    icon="pi pi-arrow-right"
    iconPos="right"
    :label="$t('Next')"
  />
</div>

    </div>
</template>
<script setup>
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js';

const {channelManagerData,onChangeDataUploadStep} = useCMDashboard()
</script>