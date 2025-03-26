<template>
    <ComDialogContent hideButtonOK @onClose="onClose"  :hideIcon="false" :loading="loading" >
    <div class="bg-card-info">

      <Message v-if="doc?.source_transaction_number">This transaction has been transferred from the <span>{{doc?.source_transaction_type}}</span>. View folio transaction
        <span class="link_line_action overflow-hidden w-min" @click="onOpenReservationFolioDetail(doc?.source_transaction_number)">{{doc?.source_transaction_number}}</span>
      </Message>

      <Message v-if="doc?.target_transaction_number && doc?.target_transaction_type=='Desk Folio'">This transaction has been transferred to <span>{{doc?.target_transaction_type}}</span>. View folio transaction
        <span class="link_line_action overflow-hidden w-min" @click="onOpenDeskFolioDetail(doc?.target_transaction_number)">{{doc?.target_transaction_number}}</span>
      </Message>

      <Message v-else="doc?.target_transaction_number && doc?.target_transaction_type=='City Ledger'">This transaction has been transferred to <span>{{doc?.target_transaction_type}}</span>. View City Ledger transaction
        <span class="link_line_action overflow-hidden w-min" @click="onOpenCityLedgerDetail(doc?.target_transaction_number)">{{doc?.target_transaction_number || doc?.transaction_number}}</span>
      </Message>

      <Message v-if="doc?.sale">This folio transaction is transferred from <span>{{doc?.account_category}}</span>. View Sale transaction
        <span class="link_line_action overflow-hidden w-min" @click="onOpenReservationFolioDetail(doc?.target_transaction_number)">{{doc?.sale}}</span>
      </Message>
      <Message v-if="doc?.parent_reference">This transaction is a sub transaction of 
        <span class="link_line_action overflow-hidden w-min" @click="onOpenFolioTransactionDetail(doc?.parent_reference)">{{doc?.parent_reference}}</span> folio transaction
      </Message>

      <div class="grid p-3">
        <div class="col">
          <div class="flex mt-2 gap-2 justify-end">
            <ComBoxStayInformation :isSlot="true" titleTooltip="Reference No." title="Ref. No" @onClick="toggle($event, 'change_ref_number')" :isAction="true" valueClass="flex-grow-0 col-8"  titleClass="col-4">
              <span>
                  <i v-if="!doc?.reference_number" class="pi pi-pencil"></i>
                  {{ doc?.reference_number ? doc?.reference_number : '...' }}
              </span>
            </ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.guest">
            <ComBoxStayInformation titleTooltip="Guest ID" title="Guest ID" :value="`${doc?.guest}`" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.guest_name">
            <ComBoxStayInformation titleTooltip="Guest Name" title="Guest Name" @onClick="onOpenGuestDetail(doc?.guest)" :value="doc?.guest_name"  :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.guest_type">
            <ComBoxStayInformation titleTooltip="Guest Type" title="Guest Type" :value="doc?.guest_type"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.nationality">
            <ComBoxStayInformation titleTooltip="Country" title="Country" :value="doc?.nationality"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.city_ledger_name">
            <ComBoxStayInformation titleTooltip="City Ledger Name" title="City Ledger Name" :value="doc?.city_ledger_name"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.city_ledger_type">
            <ComBoxStayInformation titleTooltip="City Ledger Type" title="City Ledger Type" :value="doc?.city_ledger_type"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col">
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.posting_date">
            <ComBoxStayInformation titleTooltip="Posting Date" title="Posting Date" :value="gv.dateFormat(doc?.posting_date)"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.working_date">
            <ComBoxStayInformation titleTooltip="Working Date" title="Working Date" :value="gv.dateFormat(doc?.working_date)"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.reservation">
            <ComBoxStayInformation titleTooltip="Reservation" title="Reservation" @onClick="onOpenReservationDetail(doc?.reservation)" :value="doc?.reservation"   :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.reservation_stay">
            <ComBoxStayInformation titleTooltip="Reservation Stay" title="Reservation Stay" @onClick="onOpenReservationStayDetail(doc?.reservation_stay)" :value="doc?.reservation_stay"   :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
        </div>
        <div class="col">
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.transaction_type">
            <ComBoxStayInformation titleTooltip="Transaction Type" title="Transaction Type" :value="doc?.transaction_type"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div> 
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.transaction_number && doc?.transaction_type=='Reservation Folio'">
            <ComBoxStayInformation titleTooltip="Transaction Number" title="Transaction Number" @onClick="onOpenReservationFolioDetail(doc?.transaction_number)" :value="doc?.transaction_number" :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.transaction_number && doc?.transaction_type=='City Ledger'">
            <ComBoxStayInformation titleTooltip="Transaction Number" title="Transaction Number" @onClick="onOpenCityLedgerDetail(doc?.transaction_number)" :value="doc?.transaction_number" :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div> 
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.transaction_number && doc?.transaction_type=='Desk Folio'">
            <ComBoxStayInformation titleTooltip="Transaction Number" title="Transaction Number" @onClick="onOpenDeskFolioDetail(doc?.transaction_number)" :value="doc?.transaction_number" :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div> 
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.room_type">
            <ComBoxStayInformation titleTooltip="Room Type" title="Room Type" :value="doc?.room_type"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.room_number">
            <ComBoxStayInformation titleTooltip="Room Number" title="Room Number" :value="doc?.room_number"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.business_source_type">
            <ComBoxStayInformation titleTooltip="Market Source Type" title="Market Source Type" :value="doc?.business_source_type"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2 justify-end" v-if="doc?.business_source">
            <ComBoxStayInformation titleTooltip="Business Source" title="Business Source" :value="doc?.business_source"   valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
          </div>
        </div>
      </div>
      <div class="p-3">
        <table class="p-datatable-table" style="width: 100%;">
          <thead class="bg-blue-50 border">
            <tr>
              <th class="text-left p-2 border">Account Code</th>
              <th class="p-2 border">Type</th>
              <th class="p-2 border">Qty</th>
              <th class="text-right p-2 border">Rate</th>
              <th class="text-right p-2 border">Amount</th>
              <th class="text-left p-2 border">Note</th>
            </tr>
          </thead>
          <tbody class="p-datatable-tbody">
            <tr class="bg-white	">
              <td class="text-left p-2 border">{{ `${doc?.account_code} - ${doc?.account_name}` }}</td>
              <td class="text-center p-2 border">{{ doc?.type }}</td>
              <td class="text-center p-2 border">{{ doc?.quantity }}</td>
              <td class="text-right p-2 border"><CurrencyFormat :value="doc?.input_amount" /></td>
              <td class="text-right p-2 border"><CurrencyFormat :value="doc?.total_amount" /> </td>
              <td class="text-left p-2 border max-w-15rem white-space-normal">{{ doc?.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div>
        <div class="grid p-3">
          <div class="col-6">
            <TabView lazy v-model:activeIndex="activeTab" class="tabview-custom mt-3" v-if="doc?.credit_card_number || doc?.bank_name || doc?.city_ledger_invoice || doc?.payment_by">
              <TabPanel :header="$t('Payment Information')" v-if="doc?.credit_card_number || doc?.bank_name || doc?.payment_by">
                <div class="pb-3">
                  <div class="grid w-full">
                    <div class="flex mt-2 gap-2 col-6" v-if="doc?.payment_by">
                      <ComBoxStayInformation @onClick="toggle($event, 'payment_info')" :isSlot="true" :isAction="true" valueMaxWidth="" titleTooltip="Payment By" title="Payment By"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">
                        <span>
                          <i v-if="!doc?.payment_by" class="pi pi-pencil"></i>
                          {{ doc?.payment_by ? doc?.payment_by : '...' }}
                        </span>
                      </ComBoxStayInformation> 
                    </div>
                    <div class="flex mt-2 gap-2 col-6" v-if="doc?.payment_by_phone_number">
                      <ComBoxStayInformation @onClick="toggle($event, 'payment_info')" :isSlot="true" :isAction="true" valueMaxWidth="" titleTooltip="Phone Number" title="Phone Number"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">
                        <span>
                          <i v-if="!doc?.payment_by_phone_number" class="pi pi-pencil"></i>
                          {{ doc?.payment_by_phone_number ? doc?.payment_by_phone_number : '...' }}
                        </span>
                      </ComBoxStayInformation> 
                    </div>
                  </div>

                  <div class="grid w-full">
                    <div class="flex mt-2 gap-2 col-6" v-if="doc?.credit_card_number">
                      <ComBoxStayInformation @onClick="toggle($event, 'bank_info')" :isSlot="true" :isAction="true" titleTooltip="Credit Card Number" title="Credit Card Number"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">

                        <span>
                          <i v-if="!doc?.credit_card_number" class="pi pi-pencil"></i>
                          {{ doc?.credit_card_number ? doc?.credit_card_number : '...' }}
                        </span>
                      </ComBoxStayInformation> 
                    </div>
                    <div class="flex mt-2 gap-2 col-6" v-if="doc?.card_holder_name">
                      <ComBoxStayInformation @onClick="toggle($event, 'bank_info')" :isSlot="true" :isAction="true" titleTooltip="Card Holder Name" title="Card Holder Name"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">

                        <span>
                          <i v-if="!doc?.card_holder_name" class="pi pi-pencil"></i>
                          {{ doc?.card_holder_name ? doc?.card_holder_name : '...' }}
                        </span>
                      </ComBoxStayInformation> 
                    </div>
                    <div class="flex mt-2 gap-2 col-6" v-if="doc?.bank_name">
                      <ComBoxStayInformation @onClick="toggle($event, 'bank_info')" :isSlot="true" :isAction="true" titleTooltip="Bank Name" title="Bank Name"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">

                        <span>
                          <i v-if="!doc?.bank_name" class="pi pi-pencil"></i>
                          {{ doc?.bank_name ? doc?.bank_name : '...' }}
                        </span>
                      </ComBoxStayInformation> 
                    </div>
                    <div class="flex mt-2 gap-2 col-6" v-if="doc?.credit_expired_date">
                      <ComBoxStayInformation @onClick="toggle($event, 'bank_info')" :isSlot="true" :isAction="true" titleTooltip="Credit Expired Date" title="Credit Expired Date"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">

                        <span>
                          <i v-if="!doc?.credit_expired_date" class="pi pi-pencil"></i>
                          {{ doc?.credit_expired_date ? moment(doc?.credit_expired_date).format("MMM yy") : '...' }}
                        </span>
                      </ComBoxStayInformation> 
                    </div> 
                  </div>
                </div>
              </TabPanel>
              <TabPanel :header="$t('City Ledger Invoice')" v-if="doc?.city_ledger_invoice">
                <div class="pb-3">
                  <div class="flex mt-2 gap-2 justify-end" v-if="doc?.city_ledger_invoice">
                    <ComBoxStayInformation titleTooltip="Invoice No." title="Invoice No." @onClick="onViewCityLedgerInvoiceDetail(doc?.city_ledger_invoice)" :value="doc?.city_ledger_invoice" :isAction="true" valueClass="grow col-8"  titleClass="col-4"></ComBoxStayInformation>
                  </div>
                  <div class="flex mt-2 gap-2" v-if="city_ledger_invoice_date!=''">
                    <ComBoxStayInformation valueMaxWidth="50%" titleTooltip="Issue Date" title="Issue Date"  valueClass="grow col-8 bg-gray-edoor-10"  titleClass="col-4">
                      {{gv.dateFormat(city_ledger_invoice_date)}}
                    </ComBoxStayInformation> 
                  </div> 
                </div>
              </TabPanel>
            </TabView>
            
          </div> 
          <div class="col-6"> 
            <template v-if="sub_record" v-for="(item, index) of sub_record" :key="index">
              <div class="flex mt-2 gap-2 justify-end">
                <ComBoxStayInformation valueMaxWidth="30%" :titleTooltip="`${item.account_name}`" :title="`${item.account_code} - ${item.account_name}`"  valueClass="grow col-8"  titleClass="col-4">
                  <CurrencyFormat :value="item.amount" />
                </ComBoxStayInformation> 
              </div>
            </template>  
            <div class="flex mt-2 gap-2 justify-end" v-if="doc?.total_amount">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Total Amount" title="Total Amount" valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="doc?.total_amount" />
              </ComBoxStayInformation> 
            </div>
          </div>
        </div>
      </div>


      <template v-if="product_items?.length>0"> 
        <div class="p-3">
          <p class="font-bold mb-1">Products</p>
          <table class="p-datatable-table" style="width: 100%;">
            <thead class="bg-blue-50 border">
              <tr>
                <th class="text-left p-2 border">Product Code</th>
                <th class="text-left p-2 border">Product Name</th>
                <th class="p-2 border">Qty</th>
                <th class="text-right p-2 border">Price</th>
                <th class="text-right p-2 border">Discount</th>
                <th class="text-right p-2 border">Total Amount</th>
              </tr>
            </thead>
            <tbody class="p-datatable-tbody">
              <template v-for="(item, index) of product_items" :key="index">
                <tr class="bg-white	">
                  <td class="p-2 border">{{item.product_code}}</td>
                  <td class="p-2 border">{{item.product_name}}</td>
                  <td class="p-2 border text-center">{{item.quantity}}</td>
                  <td class="p-2 border text-right"><CurrencyFormat :value="item.price" /></td>
                  <td class="p-2 border text-right"><CurrencyFormat :value="item?.discount_amount?item?.discount_amount:0" /></td>
                  <td class="p-2 border text-right"><CurrencyFormat :value="item.total_amount" /></td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </template>
      <div>
        <div class="grid p-3">
          <div class="col-6">
            <template v-if="doc?.note">
              <div>Note:</div>
              <Textarea disabled v-model="doc.note" rows="6" cols="50" />
            </template>
          </div>
          <div class="col-6">  
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.total_quantity">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Total Quantity" title="Total Quantity"  valueClass="grow col-8"  titleClass="col-4">
                {{ sale_summary.total_quantity }}
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.sub_total">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Sub Total" title="Sub Total"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.sub_total" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.service_charge">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Service Charge" title="Service Charge"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.service_charge" />
              </ComBoxStayInformation> 
            </div>
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.specific_tax">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Specific Tax" title="Specific Tax"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.specific_tax" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.total_tax">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="VAT 10%" title="VAT 10%"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.total_tax" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.product_discount">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Product Discount" title="Product Discount"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.product_discount" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.discount">
              <ComBoxStayInformation valueMaxWidth="30%" :titleTooltip="`Sale Discount ${sale_summary.discount_type=='Percent'?sale_summary.discount + '%':''}`" :title="`Sale Discount ${sale_summary.discount_type=='Percent'?sale_summary.discount + '%':''}`"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.sale_discount" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.sale_discount>0 && sale_summary?.product_discount>0">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Total Discount" title="Total Discount"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.total_discount" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.total_fee">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Total Bank Fee" title="Total Bank Fee"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.total_fee" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.tip_amount">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Tip" title="Tip"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.tip_amount" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.grand_total">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Grand Total" title="Grand Total"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.grand_total" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.total_paid">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Paid Amount (Paid to Room)" title="Paid Amount (Paid to Room)" valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.total_paid" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.balance">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Balance" title="Balance"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.balance" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.balance">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Balance" title="Balance"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.balance" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.changed_amount">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Change Amount" title="Change Amount"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.changed_amount" />
              </ComBoxStayInformation> 
            </div> 
            <div class="flex mt-2 gap-2 justify-end" v-if="sale_summary?.commission_amount">
              <ComBoxStayInformation valueMaxWidth="30%" titleTooltip="Commission Amount" title="Commission Amount"  valueClass="grow col-8"  titleClass="col-4">
                <CurrencyFormat :value="sale_summary?.commission_amount" />
              </ComBoxStayInformation> 
            </div> 
             
             
          </div>
        </div>
      </div> 
    </div> 
    <template #footer-left>
      <Button @click="test">Test</Button>
      <Button v-if="doc?.show_print_preview!=0" icon="pi pi-print" class="border-none" @click="onPrintFolioTransaction" :label="$t('Print')" :disabled="loading"></Button>
      <Button icon="pi pi-file-edit" class="border-none" @click="onEditFolioTransaction" :label="$t('Edit')" :disabled="loading"></Button>
    </template> 
    <OverlayPanel ref="op">
      <ComOverlayPanelContent title="" :width="isMobile ? '100%' : '50rem'" :loading="isLoading" @onSave="onSave" @onCancel="onCloseRef">
        <div class="grid">
          <template v-if="overLayName=='change_ref_number'">
            <div class="col-6">
              <label>{{ $t('Ref. No') }} </label><br/>
              <InputText v-model="doc.reference_number" class="w-full"/>
            </div> 
          </template>
          <template v-if="overLayName=='payment_info'">
            <div class="col-6">
              <label>{{ $t('Payment By') }} </label><br/>
              <InputText v-model="doc.payment_by" class="w-full"/>
            </div>
            <div class="col-6">
              <label>{{ $t('Payment(Phone No.)') }} </label><br/>
              <InputText v-model="doc.payment_by_phone_number" class="w-full"/>
            </div>
          </template>
          <template v-if="overLayName=='bank_info'">
            <div class="col-6">
              <label>{{ $t('Credit Card Number') }} </label><br/>
              <InputText v-model="doc.credit_card_number" class="w-full"/>
            </div>
            <div class="col-6">
              <label>{{ $t('Card Holder Name') }} </label><br/>
              <InputText v-model="doc.card_holder_name" class="w-full"/>
            </div>
            <div class="col-6">
              <label>{{ $t('Bank Name') }} </label><br/>
              <InputText v-model="doc.bank_name" class="w-full"/>
            </div>
            <div class="col-6">
              <label>{{ $t('Credit Expired Date') }} </label><br/> 
              <Calendar class="w-full" v-model="doc.credit_expired_date" view="month" dateFormat="mm/yy" showIcon showButtonBar  />
            </div>
          </template>
        </div>
      </ComOverlayPanelContent>
    </OverlayPanel>
  </ComDialogContent>
    
</template>
<script setup>

import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComReportServerModal  from "@/components/ComReportServerModal.vue";
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import {ref,getDoc,onMounted,getApi,inject,useDialog,updateData} from "@/plugin"
import BtnCloseIcon from '@/assets/svg/icon-close.svg' 
import {i18n} from '@/i18n';
 
import {useApp} from "@/hooks/useApp"
const {isCityLedgerInvoiceDetailOpen} = useApp()


const gv = inject('$gv');
const loading = ref(true)
const doc = ref()
const sub_record = ref()
const product_items = ref()
const dialogRef = inject("dialogRef") 
const dialog = useDialog()
const sale_summary = ref()
const city_ledger_invoice_date = ref()
const overLayName = ref("")
const op = ref();
const moment = inject("$moment")

const toggle = ($event, name) => {
    overLayName.value = name
    op.value.toggle($event);
}

async function test(){
  

}

const setting =window.setting
const { t: $t } = i18n.global;

function loadData(){
    if (dialogRef.value.data.folio_transaction_number) {
    loading.value = true
    getApi("reservation.get_folio_transaction_detail", {
      name: dialogRef.value.data.folio_transaction_number
    })
      .then((result) => { 
        doc.value = result.message.folio_transaction
        sub_record.value = result.message.sub_record
        doc.value.tax_rule_data = JSON.parse(result.message.folio_transaction.tax_rule_data)
        product_items.value = result.message.product_items
        sale_summary.value = result.message.sale
        city_ledger_invoice_date.value = result.message.city_ledger_invoice_date
 
        loading.value = false
      }).catch((err) => {
        loading.value = false
      })
  }
}

onMounted(() => {
    loadData();
})

const onClose = () => {

    dialogRef.value.close()
}

const onOpenGuestDetail = (id) => {
  window.postMessage('view_guest_detail' + "|" + id, '*')
}
const onOpenReservationDetail = (id) => {
  window.postMessage('view_reservation_detail' + "|" + id, '*')
}
const onOpenReservationStayDetail = (id) => {
  window.postMessage('view_reservation_stay_detail' + "|" + id, '*')
}
const onOpenReservationFolioDetail = (id) => {
  window.postMessage('view_folio_detail' + "|" + id, '*')
}

const onOpenFolioTransactionDetail = (id) => {
  window.postMessage('view_folio_transaction_detail' + "|" + id, '*')
}

const onOpenCityLedgerDetail = (id) => {
  window.postMessage('view_city_ledger_detail' + "|" + id, '*')
}

const onOpenDeskFolioDetail = (id) => {
  window.postMessage('view_desk_folio_detail' + "|" + id, '*')
}

const onViewCityLedgerInvoiceDetail = (id) => {
  if(isCityLedgerInvoiceDetailOpen.value){
    dialogRef.value.close()
  }
  else {
    window.postMessage('view_city_invoice_detail' + "|" + id, '*')
  }
}



function onPrintFolioTransaction() { 
  const dialogRef = dialog.open(ComReportServerModal, {
    data: {
      doctype: "Folio Transaction",
      name: doc.value.name,
      report_path: doc.value.print_format,
      params: [
        { name: 'folio_transaction', values: [doc.value.name] }
      ]
    },
    props: {
      header: 'Print Preview',
      style: {
        width: '80vw',
      },
      position: "top",
      modal: true,
      breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
    },
  })
}


function onEditFolioTransaction() {
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_transaction_number: doc.value.name,
            reservation_stay:doc.value.reservation_stay
        },
        props: {
            header: 'Edit Folio Transaction - ' + doc.value.name,
            style: {
                width: '60vw',
            },
            modal: true,
            position:'top',
            closeOnEscape: false,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                //load folio list and folio transaction 
 
                window.postMessage({action:"load_reservation_folio_list"},"*")
                window.postMessage({action:"load_reservation_stay_folio_list"},"*")
                window.postMessage({action:"load_folio_transaction"})


            }

        }
    })
}

function onCloseRef(result){
    op.value.hide()
} 
</script>