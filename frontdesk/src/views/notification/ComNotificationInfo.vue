<template>
            <table>
            <ComStayInfoNoBox :label="doc.document_type">
              <div class="flex gap-2">
                  <span class="link_line_action" @click="onViewDetail(doc.document_type,doc.document_name)" >{{ doc.document_name }}</span>
                    <span class="px-2 rounded-lg me-2 text-white p-1px" :style="{background:data.status_color}">
                      {{ data.reservation_status }}
                    </span>
              </div>
                  
                
                  </ComStayInfoNoBox>
            <ComStayInfoNoBox :label="$t('Guest')">
                    <div class="link_line_action" @click="onViewDetail('guest',data.guest)" >{{ data.guest_name }}</div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox :label="$t('Business Source')" >
              {{ data.business_source }}
             </ComStayInfoNoBox>
            <ComStayInfoNoBox :label="$t('Reservation Type')">
              {{ data.reservation_type }}
            </ComStayInfoNoBox>  
            <ComStayInfoNoBox :label="$t('Arrival Date')" >
              {{ data.arrival_date }}
            </ComStayInfoNoBox>
            <ComStayInfoNoBox :label="$t('Departure Date')" >
              {{ data.departure_date }}
            </ComStayInfoNoBox>
            <ComStayInfoNoBox :label="$t('Room')" >
              {{ data.room_type_alias }} / {{ data.rooms }} 
             </ComStayInfoNoBox>
            </table> 
</template>
<script setup>
import { inject, ref,  getDoc, onMounted , watch } from '@/plugin'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const data = ref({})
const props = defineProps({
  doc: {
    type: Object,
    required: true,
    default: () => ({})
  },
});
function onViewDetail(doctype,name){
   window.postMessage(`view_${doctype.toLowerCase().replaceAll(" ","_")}_detail|${name}`,"*")
   console.log(`view_${doctype.toLowerCase().replaceAll(" ","_")}_detail|${name}`)
}

const fetchData = async () => {
  if (props.doc && props.doc.document_type && props.doc.document_name) {
    try {
      const result = await getDoc(props.doc.document_type, props.doc.document_name);
      data.value = result;
    } catch (err) {
      console.error('Error fetching data:', err);
    }
  } 
};

watch(
  () => props.doc,
  (newDoc) => {
    if (newDoc && newDoc.document_type && newDoc.document_name) {
      console.log('props.doc is ready, fetching data...');
      fetchData();
    } else {
      console.warn('props.doc is missing required properties.');
    }
  },
  { immediate: true }
);

// Optional: You can also fetch the data immediately in `onMounted` if props.doc is initially available
onMounted(() => {
  if (props.doc && props.doc.document_type && props.doc.document_name) {
    fetchData(); // Fetch data if `props.doc` is already available on mount
  } else {
    console.warn('props.doc is not ready on mount.');
  }
})
</script>