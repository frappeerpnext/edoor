<template>
    <div class="grid w-full">
        <div class="col-12 lg:col" v-if="hasFilter('filter_date_by')">
            <label> {{ $t('Filters') }} </label><br/>
            <ComSelect class="auto__Com_Cus w-full" v-model="filter.filter_date_by" placeholder="Filter By Date"
                                :options="['Arrival Date', 'Departure Date', 'Reservation', 'Stay']" :clear="false" />
        </div> 
        
        <div class="col-12 lg:col-3" v-if="hasFilter('start_date')">
            <label> {{ $t('Start Date') }} </label><br/>
            <Calendar showButtonBar panelClass="no-btn-clear" @date-select="onSelectStartDate" class="w-full" :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date" dateFormat="dd-mm-yy"
                showIcon />
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('cashier_shift')">
            <label> {{ $t('Cashier Shift') }} </label><br>
            <ComAutoComplete v-model="filter.cashier_shift" placeholder="Cashier Shift" doctype="Cashier Shift"
            class="auto__Com_Cus w-full" :isMultipleSelect="false" maxWidth="30rem" :maxSelectLabel="10" 
            :filters="{ is_edoor_shift:['=',1],posting_date:filter.start_date}"/>
        </div>
        <div class="col-12 lg:col-3" v-if="hasFilter('end_date')">
            <label> {{ $t('End date') }} </label><br>
            <Calendar showButtonBar panelClass="no-btn-clear" class="w-full" :min-date="filter.start_date" :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date" dateFormat="dd-mm-yy"
                showIcon />
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('reservation')">
            <label> {{ $t('Reservation') }} </label><br>
            <ComSelect v-model="filter.reservation" placeholder="Reservation" doctype="Reservation"
            class="auto__Com_Cus w-full" :isMultipleSelect="false" maxWidth="30rem" :maxSelectLabel="10" />
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('reservation_stay')">
            <label>{{$t('Reservation Stay') }}</label><br>
            <ComSelect v-model="filter.reservation_stay" placeholder="Reservation Stay" doctype="Reservation Stay"
            class="auto__Com_Cus w-full" :isMultipleSelect="false" maxWidth="30rem" :maxSelectLabel="10" />
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('select_filter')">
            <label>{{ $t('Select Filter') }}</label><br>
            <ComSelect class="w-full"  v-model="filter.select_filter" placeholder="Select Filter"
            :options="['Reservation','Reservation Stay','Reservation Room Rate','Guest','Reservation Folio','Folio Transaction']" />
        </div>
        
        <div class="col-12 lg:col" v-if="hasFilter('reservation_type')">
            <label>{{ $t('Reservation Type') }}</label><br>
            <ComSelect class="w-full"   v-model="filter.reservation_type" placeholder="Select Reservation Type" :showClear="true"
            :options="['FIT','GIT']" />
        </div>
        
        <div class="col-12 lg:col"  v-if="hasFilter('reservation_status')">
            <label> {{ $t('Reservation Status') }} </label><br>
            <ComSelect v-model="filter.reservation_status" placeholder="Reservation Status" doctype="Reservation Status"
            class="auto__Com_Cus w-full" :isMultipleSelect="true" maxWidth="30rem" :maxSelectLabel="10" />
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('room_type')">
            <label> {{ $t('Room Type') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
            optionLabel="room_type" optionValue="room_type"
            extraFields="room_type"
                v-model="filter.room_type"   placeholder="Room Type" doctype="Room Type"
                :filters="{ property: property.name }" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('room_name_types')">
            <label> {{ $t('Room Types') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
            optionLabel="room_type" optionValue="name"
            extraFields="room_type"
                v-model="filter.room_name_types"   placeholder="Room Type" doctype="Room Type"
                :filters="{ property: property.name }" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('rooms')">
            <label> {{ $t('Room') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
            optionLabel="room_number" optionValue="room_number"
            extraFields="room_number"
                v-model="filter.rooms"   placeholder="Room" doctype="Room"
                :filters="{ property: property.name }" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('building')">
            <label> {{ $t('Building') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
                v-model="filter.building"   placeholder="building" doctype="Building"
                :filters="{ property: property.name }" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('floor')">
            <label> {{ $t('Floor') }} </label><br>
            
            <ComSelect class="auto__Com_Cus w-full" 
                v-model="filter.floor" placeholder="floor" doctype="Floor"
                :filters="[['property', '=', property.name]]" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('housekeeper')">
            <label> {{ $t('Housekeeper') }} </label><br>
            
            <ComSelect class="auto__Com_Cus w-full" 
                v-model="filter.housekeeper"   placeholder="housekeeper" doctype="Housekeeper"
                maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('housekeeping_status')">
            <label> {{ $t('Housekeeping Status') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
                v-model="filter.housekeeping_status"   placeholder="status" doctype="Housekeeping Status"
                    :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('account_name')">
            <label> {{ $t('Account Name') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
            optionLabel="account_name" optionValue="account_name"
            extraFields="account_name"
                v-model="filter.account_name"   placeholder="Account Name" doctype="Account Code"
                :filters="{ parent_account_code: ['=','10200'] }" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
        </div>
       
        <div class="col-12 lg:col"  v-if="hasFilter('parent_account')">
            <label> {{ $t('Parent Account') }} </label><br>
            <ComAutoComplete v-model="filter.parent_account" placeholder="Parent Account Code" doctype="Account Code"
            class="auto__Com_Cus w-full" :isMultipleSelect="false" maxWidth="30rem" :maxSelectLabel="10" 
            :filters="{ name:['!=','All Account Code']}"/>
        </div>

        <div class="col-12 lg:col"  v-if="hasFilter('sale')">
            <label> {{ $t('Sale Number') }} </label><br>
            
            <ComAutoComplete        class="auto__Com_Cus w-full" 
                v-model="filter.sale"   placeholder="Sale Number" doctype="Sale"
                :filters="{ business_branch:property.name}" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" />
        </div>

        <div class="col-12 lg:col"  v-if="hasFilter('arrival_modes')">
            <label> {{ $t('Arrival Mode') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
                v-model="filter.arrival_modes"   placeholder="Arrival Mode" doctype="Transportation Mode"
                ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('departure_mode')">
            <label> {{ $t('Departure Mode') }} </label><br>
            
            <ComSelect        class="auto__Com_Cus w-full" 
                v-model="filter.departure_mode"   placeholder="Departure Mode" doctype="Transportation Mode"
                ></ComSelect>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('business_source')">
            <label> {{ $t('Business Source') }} </label><br>
            <ComAutoComplete v-model="filter.business_source" placeholder="Business Source" doctype="Business Source"
            class="auto__Com_Cus w-full" :filters="{ property: property.name }" />
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('ledger_type')">
            <label> {{ $t('Ledger Type') }} </label><br>
            <ComSelect class="w-full"   v-model="filter.ledger_type" placeholder="Ledger Type" :showClear="true"
            :options='["Reservation Folio","Desk Folio","City Ledger","Deposit Ledger","Payable Ledger","Cashier Shift"]' :isMultipleSelect="true"/>
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('ledger_types')">
            <label> {{ $t('Ledger Type') }} </label><br>
            <ComSelect class="w-full"   v-model="filter.ledger_types" placeholder="Ledger Type" :showClear="true"
            :options='["Reservation Folio","Desk Folio","City Ledger","Deposit Ledger","Payable Ledger","Cashier Shift"]' :isMultipleSelect="false"/>
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('working_day')">
            <label> {{ $t('Working Day') }} </label><br>
            <ComAutoComplete v-model="filter.working_day" placeholder="working day" doctype="Working Day"
            class="auto__Com_Cus w-full" />
        </div>
        <div class="col-12 lg:col mt-4"  v-if="hasFilter('group_by_ledger_type')">
            <div class="h-full" >
                <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <div>
                    <label for="filter_is_active" class="font-medium cursor-pointer">Group by Leger Name</label>
                </div>
                <div>
                    <Checkbox class="mx-3" v-model="filter.group_by_ledger_type" :binary="true" trueValue="1"
                            falseValue="0" /> 
                </div>
                </div>
            </div>   
        </div>
        
        <div class="col-12 lg:col mt-4"  v-if="hasFilter('show_account_code')">
            <div class="h-full" >
                <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <div>
                    <label for="filter_is_active" class="font-medium cursor-pointer"> {{ $t('Show Account Code') }} </label>
                </div>
                <div>
                    <Checkbox class="mx-3" v-model="filter.show_account_code" :binary="true" trueValue="1"
                            falseValue="0" /> 
                </div>
                </div>
            </div>   
        </div>
    </div>
    <div class="grid w-full">
        <div class="col-12 lg:col" v-if="hasFilter('business_source_type')">
            <label> {{ $t('Business Source Type') }} </label><br>
            <ComAutoComplete v-model="filter.business_source_type" placeholder="Business Source Type" doctype="Business Source Type"
            class="auto__Com_Cus w-full" />
        </div>
        <div class="col-12 lg:col mt-4"  v-if="hasFilter('is_active_reservation')">
            <div class="h-full" >
                <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <div>
                    <label for="filter_is_active" class="font-medium cursor-pointer"> {{ $t('Is Active Reservation') }} </label>
                </div>
                <div>
                    <Checkbox input-id="filter_is_active" class="mx-3" v-model="filter.is_active_reservation" :binary="true" trueValue="1"
                            falseValue="0" /> 
                </div>
                </div>
            </div>   
        </div>
        <div class="col-12 lg:col mt-4"  v-if="hasFilter('show_cash_float')">
            <div class="h-full" >
                <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <div>
                    <label for="filter_is_active" class="font-medium cursor-pointer"> {{ $t('Show Cash Float') }} </label>
                </div>
                <div>
                    <Checkbox class="mx-3" v-model="filter.show_cash_float" :binary="true" trueValue="1"
                            falseValue="0" /> 
                </div>
                </div>
            </div>   
        </div>
        <div class="col-12 lg:col mt-4"  v-if="hasFilter('show_cash_count')">
            <div class="h-full" >
                <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <div>
                    <label for="filter_is_active" class="font-medium cursor-pointer">{{ $t('Show Cash Count') }}</label>
                </div>
                <div>
                    <Checkbox class="mx-3" v-model="filter.show_cash_count" :binary="true" trueValue="1"
                            falseValue="0" /> 
                </div>
                </div>
            </div>   
        </div>
        <div class="col-12 lg:col mt-4"  v-if="hasFilter('show_summary')">
            <div class="h-full" >
                <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <div>
                    <label for="filter_is_active" class="font-medium cursor-pointer"> {{ $t('Show Summary') }} </label>
                </div>
                <div>
                    <Checkbox input-id="filter_is_active" class="mx-3" v-model="filter.show_summary" :binary="true" trueValue="1"
                            falseValue="0" /> 
                </div>
                </div>
            </div>   
        </div>
        
        <div class="col-12 lg:col" v-if="hasFilter('guest')">
            <label> {{ $t('Guest') }} </label><br/>
            <ComSelect        class="auto__Com_Cus w-full" 
            optionLabel="customer_name_en" optionValue="name"
            extraFields="customer_name_en"
                v-model="filter.guest"   placeholder="Guest" doctype="Customer"></ComSelect>
        </div> 
        <div class="col-12 lg:col" v-if="hasFilter('guest_type')">
            <label> {{ $t('Guest Type') }} </label><br>
            <ComAutoComplete v-model="filter.guest_type" placeholder="Guest Type" doctype="Customer Group"
            class="auto__Com_Cus w-full" />
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('nationality')">
            <label> {{ $t('Nationality') }} </label><br>
            <ComAutoComplete v-model="filter.nationality" placeholder="Nationality" doctype="Country"
            class="auto__Com_Cus w-full" />
        </div>
        <div class="col-12 lg:col"  v-if="hasFilter('city_ledger')">
            <label> {{ $t('City Ledger') }} </label><br>
            <ComAutoComplete v-model="filter.city_ledger" placeholder="City Ledger" doctype="City Ledger"
            class="auto__Com_Cus w-full" />
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('account_code')">
            <label> {{ $t('Account Code') }} </label><br>
            <ComAutoComplete v-model="filter.account_code" placeholder="Account Code" doctype="Account Code"
            class="auto__Com_Cus w-full" />
        </div>
        
        <div class="col-12 lg:col"  v-if="hasFilter('account_category')">
            <label> {{ $t('Account Category') }} </label><br>
            <ComAutoComplete v-model="filter.account_category" placeholder="Account Category" doctype="Account Category"
            class="auto__Com_Cus w-full" :isMultipleSelect="false" maxWidth="30rem" :maxSelectLabel="10" />
        </div>
        
        
        <div class="col-12 lg:col" v-if="hasFilter('select_user')">
            <label> {{ $t('Select User') }} </label><br/>
            <ComSelect        class="auto__Com_Cus w-full" 
            optionLabel="username" optionValue="name"
            extraFields="username"
                v-model="filter.select_user"   placeholder="Select User" doctype="User"></ComSelect>
        </div> 
        <div class="col-12 lg:col" v-if="hasFilter('group_by')">
            <label> {{ $t('Group By') }} </label><br/>
            <ComSelect class="auto__Com_Cus w-full" v-model="filter.group_by" placeholder="Group By"
                :options="['Arrival Date', 'Departure Date', 'Reservation','Reservation Date','Reservation Type','Guest','Room Type','Business Source','Business Source Type','Nationality','Rate Type','Reservation Status']" 
                    />
        </div> 
        <div class="col-12 lg:col" v-if="hasFilter('order_by')">
            <label> {{ $t('Order By') }} </label><br/>
            <ComSelect class="auto__Com_Cus w-full" v-model="filter.order_by" placeholder="Order By"
                :options="['Last Update On', 'Created On', 'Reservation','Reservation Stay','Arrival Date','Departure Date','Room Type','Reservation Status']" 
                :default="['Last Update On']" 
                :clear="false"/>
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('audit_order')">
            <label> {{ $t('Order By') }} </label><br/>
            <ComSelect class="auto__Com_Cus w-full" v-model="filter.audit_order" placeholder="Order By"
                :options="['Last Update On', 'Created On', 'Reference Document','Reference Name','Audit Date','Subject','Description','Created By']" 
                :clear="false"/>
        </div>
        <div class="col-12 lg:col" v-if="hasFilter('sort_order')">
            <label> {{ $t('Sort Order') }} </label><br/>
            <ComSelect class="auto__Com_Cus w-full" v-model="filter.sort_order" placeholder="Sort"
                :options="['ASC', 'DESC']" 
                :clear="false" />
        </div> 
        <div class="col-12 lg:col" v-if="hasFilter('row_group')">
            <label>{{ $t('Group By') }}</label><br/>
            <ComSelect class="auto__Com_Cus w-full" v-model="filter.row_group" placeholder="Group By"
                :options="['Date', 'Month', 'Room Type' , 'Reservation Type','Business Source','Business Source Type','Guest Type','Nationality']" 
                />
        </div>
        
    </div>
</template>
<script setup> 
import { ref } from "@/plugin"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const window = JSON.parse(localStorage.getItem("edoor_working_day"))
const property = setting.property
const props = defineProps({
    selectedReport: Object,
    filter: Object
})
 
const hasFilter = ref((f) => { 
    if (props.selectedReport) {
        if(props.selectedReport.filter_option){ 
            return props.selectedReport.filter_option.split(",").filter(x=>x.trim()==f.trim()).length > 0
        } 
    }
    return false 
});
</script>