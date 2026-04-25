<template>
    <div class="grid p-5 m-0 flex justify-content-center">

        <!-- Basic Information -->
        <div class="col-6 card">
            <div class="card-inner "> 
                <h3>{{$t('Rate Plan Info')}} </h3>
                <div class="form-row"> 
                    <div class="form-group" style="flex:1;"> 
                        <div class="status-box">
                            <div class="status-text">
                                <strong>{{$t('Rate Plan Status')}}</strong>
                                {{rateInfo.rate_type?.disabled!=1? `${$t('Currently active and bookable')}`:`${$t('Currently inactive and unbookable')}`}}
                            </div>
                            <div class="switch" :class="rateInfo.rate_type?.disabled!=1?'active':''"></div>
                        </div>
                    </div>
                </div>  
                <div class="form-row"> 
                    <div class="form-row">
                        <div class="form-group">
                            <label>{{$t('Rate Type')}}</label>
                            <input :value="rateInfo.rate_type?.name" readonly/>
                        </div> 
                    </div>
                    <div class="form-group" v-if="rateInfo.cm_rate_plan_list?.rate_plan_name">
                        <label>{{$t('Channel Rate Type')}}</label>
                        <input :value="rateInfo.cm_rate_plan_list?.rate_plan_name" readonly/>
                    </div>

                    <div class="form-group" v-if="rateInfo.cm_rate_plan_list?.cm_rate_plan">
                        <label>{{ $t('Channel Rate Code') }}</label>
                        <input :value="rateInfo.cm_rate_plan_list?.cm_rate_plan" readonly/>
                    </div>
                </div>  
                <div class="form-row">
                    <div class="form-group" style="flex:1;" v-if="rateInfo.rate_type?.room_types.length>0">
                        <label>{{$t('Available Room Types')}}</label>
                        <div class="checkbox-group"> 
                            <DataTable :value="rateInfo.rate_type?.room_types" tableStyle="min-width: 30rem">
                                <Column header="Room Type">
                                    <template #body="slotProps">
                                        {{roomTypes
                                                .filter(name => name.edoor_room_type === slotProps.data.room_type)
                                                .map(name => name.room_type_name)
                                                .join('')
                                            }}

                                    </template>
                                </Column>
                                <Column header="Code" >
                                    <template #body="slotProps">
                                        {{roomTypes
                                                .filter(name => name.edoor_room_type === slotProps.data.room_type)
                                                .map(name => name.cm_room_type)
                                                .join('')
                                            }}
                                    </template>
                                </Column>
                                <Column header="Min Rate" class="text-center">
                                    <template #body="slotProps">
                                        <div class="col"><Chip><CurrencyFormat :value="slotProps.data.min_rate"/></Chip></div>
                                    </template>
                                </Column> 
                            </DataTable> 
                        </div>
                    </div> 
                    <div class="form-group" style="flex:1;" v-if="rateInfo.rate_type?.business_source.length>0">
                        <label>{{$t('Available Business Source')}}</label>
                        <div class="checkbox-group">
                            <div class="flex flex-column gap-4">
                                <template v-for="bs in rateInfo.rate_type?.business_source"> 
                                    <div class="flex gap-1">
                                        <Checkbox v-model="checked" :binary="true" :trueValue="1" :falseValue="0" @change="checked = 1"/> 
                                        <label>
                                            {{bs.business_source}}
                                        </label> 
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div> 
                </div> 
                <div class="form-row" > 
                    <div class="form-group" style="flex:1" v-if="rateInfo?.room_rate_min_max_date?.start_date">
                        <label>{{$t("Start Sell Date")}}</label>
                        <input :value="moment(rateInfo?.room_rate_min_max_date?.start_date).format('DD-MM-yyyy')" readonly/>
                    </div> 
                    <div class="form-group" style="flex:1" v-if="rateInfo?.room_rate_min_max_date?.end_date">
                        <label>{{$t("Stop Sell Date")}}</label>
                        <input :value="moment(rateInfo?.room_rate_min_max_date?.end_date).format('DD-MM-yyyy')" readonly/>
                    </div>   
                </div>
    
                <div class="form-group">
                    <label>{{$t('Note')}}</label>
                    <textarea readonly>{{ rateInfo.rate_type?.note || ''}}</textarea>
                </div> 
            </div>
        </div>   
    </div>   
    
</template>
<script setup>
import { onMounted, ref, inject } from 'vue';
import { useRatePlan } from '../hooks/useRatePlan'; 
import {i18n} from '@/i18n'; 
const moment= inject("$moment")
const { t: $t } = i18n.global;
const { 
        rateInfo, 
        roomTypes
    } = useRatePlan();    
const checked = ref(1)
onMounted(() => {     
})
</script>
<style scoped> 
.card .card-inner {
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}
 
.card h3 {
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
}

.form-group {
    margin-bottom: 15px;
}

.form-row {
    display: flex;
    gap: 15px;
}

.form-group label {
    display: block;
    font-size: 12px;
    margin-bottom: 6px;
    color: #666;
    font-weight: 500;
}

input,
select,
textarea {
    width: 100%;
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid #e0e4ef;
    background: #f9fafc;
    font-size: 14px;
    transition: 0.2s;
}

input:focus,
select:focus,
textarea:focus {
    outline: none;
    border-color: #e0e4ef;
    background: #f9fafc;
}

textarea {
    resize: none;
    height: 70px;
}

.checkbox-group {
    background: #f9fafc;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #e0e4ef;
}

.checkbox-group label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
}

.toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f9fafc;
    border: 1px solid #e0e4ef;
    padding: 10px 12px;
    border-radius: 10px;
}

.switch {
    width: 40px;
    height: 20px;
    background: #dcdff1;
    border-radius: 20px;
    position: relative;
    cursor: pointer;
}

.switch::after {
    content: '';
    width: 16px;
    height: 16px;
    background: white;
    position: absolute;
    top: 2px;
    left: 2px;
    border-radius: 50%;
    transition: 0.3s;
}

.switch.active {
    background: #6c63ff;
}

.switch.active::after {
    left: 22px;
}

.status-box {
    background: #eef0ff;
    border-radius: 12px;
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.status-text {
    font-size: 13px;
    color: #555;
}

.status-text strong {
    display: block;
    color: #333;
}

.small-row {
    display: flex;
    gap: 10px;
    align-items: center;
}

.multiplier {
    display: flex;
    align-items: center;
    gap: 8px;
}

.multiplier span {
    font-size: 18px;
    color: #888;
}
</style>