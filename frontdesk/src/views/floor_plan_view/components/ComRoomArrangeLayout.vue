<template>
  <div @contextmenu="onOpenMenu" style="height: 100%; width: 100%">
    <template v-if="room.element">
      <div
        style="height: 100%; width: 100%"
        class="floor-plan-element"
        @click="toggle"
        v-html="room.element"
      ></div>
    </template>
    <template v-else>
      <div class="room-floor-plan h-full w-full text-lg">
      {{ room.room_type_alias }} - {{ room.room_number }}
      </div>
    </template>
  </div>

  <ContextMenu ref="menu" :model="contextMenuItems" />

  <OverlayPanel
    ref="op"
    class="style_panel bg-white p-2 rounded-lg shadow-lg max-w-md w-full"
  >
  <div class="grid w-full">
    <div class="text-xl font-semibold">Style element</div>
    <hr class="w-full">
    <div class="col-12 flex gap-2">
      <div>
        <label>Input Text</label>
        <InputText class="w-full" type="text" v-model="elementStyle.elementText" />
      </div>
      <div>
       <label>Color</label> 
        <div class="w-3rem h-3rem rounded-lg border-1" style="border-color: #a0bde0;"
        @click="toggleColor($event , 'color')" :style="{ background: elementStyle.color }"></div>
      </div>
    </div>
    <div class="col-12">
      <label>Font Size - {{ elementStyle.fontSize }} px</label>
      <Slider
        v-model="elementStyle.fontSize"
        :min="5"
        :max="50"
        class="w-full mt-2"
      />
    </div> 
    <div class="col-12">
      <label>TextTransform</label>
      <ComSelect
        inputClass="w-full"
        v-model="elementStyle.textTransform"
        :options="['none', 'uppercase', 'lowercase', 'capitalize','inherit']"
      />
    </div>
    <div class="col-12">
     <label>Text Effect</label> 
      <ComSelect
      
        v-model="elementStyle.textEffect"
        :options="['none', 'rotate']"
      />
    </div>
    <div>
      
    </div>
    <div class="col-6">
      <label>Justify Content</label>
      <ComSelect
        v-model="elementStyle.justifyContent"
        :options="['left', 'center', 'right']"
        inputClass="w-full"
      />
    </div>
    <div class="col-6">
      <label>Align Items</label>
      <ComSelect
        v-model="elementStyle.alignItems"
        :options="alignItemsOptions"
        optionValue="value" optionLabel="label"
        inputClass="w-full"
      />
    </div>
    <div class="col-12" v-if="elementStyle.textEffect === 'rotate'">
      <label>Rotate Degree - {{ elementStyle.rotateDegree }}°</label>
      <Slider
        v-model="elementStyle.rotateDegree"
        :min="0"
        :max="360"
        class="w-full mt-2"
      />
    </div> 
    <hr class="w-full mt-2 mb-1">
    <div class="flex col-12 gap-2">
<div class="col-6 p-0 ">
      <label>Background Color</label>
      <div class="w-full h-3rem rounded-lg border-1" style="border-color: #a0bde0;"
      @click="toggleColor($event , 'background')" :style="{ background: elementStyle.background }"></div>
    </div>
    <div class="col-6 p-0">
      <label>Border Color</label>
      <div class="w-full h-3rem rounded-lg border-1" style="border-color: #a0bde0;"
      @click="toggleColor($event , 'borderColor')" :style="{ background: elementStyle.borderColor }"></div>
    </div>
    </div>
      <div class="col-12">
        <label>Border Width</label>
      <Slider
        v-model="elementStyle.borderWidth"
        :min="1"
        :max="10"
        class="w-full mt-"
      />
      </div>
  </div>
    

 

    
    



   
    
  


    <OverlayPanel ref="overlay">
            <ComColorPicker v-if="overlayName == 'color'" v-model="elementStyle.color" />
            <ComColorPicker v-if="overlayName == 'background'" v-model="elementStyle.background" />
            <ComColorPicker v-if="overlayName == 'borderColor'" v-model="elementStyle.borderColor" />
    </OverlayPanel>
  </OverlayPanel>
</template>

<script setup>
import { ref, watch, defineEmits, defineProps } from "vue";
import { i18n } from "@/i18n";
import ContextMenu from "primevue/contextmenu";
import ColorPicker from "primevue/colorpicker";
import Slider from "primevue/slider";

const op = ref();
const overlayName = ref("");
const emit = defineEmits(["onDelete"]);
const { t: $t } = i18n.global;

const props = defineProps({
  room: Object,
});
const overlay = ref();
const toggleColor = ($event,NameEvent) => {
    overlayName.value = NameEvent
    overlay.value.toggle($event);
}
const alignItemsOptions = [
  { value: 'start', label: 'Top' },
  { value: 'center', label: 'Center' },
  { value: 'end', label: 'Bottom' }
];
const menu = ref();
const elementStyle = ref({
  color: "000000",
  background: "ffffff",
  borderColor: "000000",
  justifyContent: "center",
  fontSize: 10,
  alignItems: "center",
  borderWidth: 1,
  rotateDegree: 0,
  textEffect: "none",
  textTransform: "none",
  elementText: "",
});

let element = null;

const toggle = (event) => {
  const activeElement = document.querySelector(
    ".drv-active .floor-plan-element div"
  );
  if (activeElement) {
    element = activeElement;
    const computedStyles = window.getComputedStyle(element);

    Object.keys(elementStyle.value).forEach((key) => {
      if (key === "color" || key === "background" || key === "borderColor") {
        elementStyle.value[key] = computedStyles[key].replace("#", "");
      } else if (key === "borderWidth" || key === "fontSize") {
        elementStyle.value[key] = computedStyles[key].replace("px", "");
      } else if (key === "rotateDegree") {
        elementStyle.value[key] =
          computedStyles.transform.match(/rotate\((\d+)deg\)/)?.[1] || 0;
      } else if (key !== "elementText") {
        elementStyle.value[key] = computedStyles[key];
      }
    });
    elementStyle.value.elementText = element.textContent;
    op.value.toggle(event);
  }
};

const contextMenuItems = ref([
  {
    label: $t("Send to Back"),
    icon: "pi pi-angle-double-down",
    command: () => {
      if ((props.room.z_index || 0) > 0) {
        props.room.z_index -= 1;
      }
    },
  },
  {
    label: $t("Bring to Front"),
    icon: "pi pi-angle-double-up",
    command: () => {
      props.room.z_index = (props.room.z_index || 0) + 1;
    },
  },
]);

if (props.room.element) {
  contextMenuItems.value.push({
    label: $t("Delete"),
    icon: "pi pi-trash",
    command: () => {
      props.room.is_deleted = 1;
    },
  });
}

watch(elementStyle.value, () => {
  console.log(elementStyle.value.color)
  if (element) {
    Object.keys(elementStyle.value).forEach((key) => {
      if (key === "borderWidth" || key === "fontSize") {
        element.style[key] = `${elementStyle.value[key]}px`;
      } else if (key === "rotateDegree") {
        element.style.transform = `rotate(${elementStyle.value[key]}deg)`;
      } else if (key === "elementText") {
        element.textContent = elementStyle.value[key];
      } else {
        element.style[key] = elementStyle.value[key];
      }
    });
    props.room.element = element.outerHTML;
  }
});

const onOpenMenu = (event) => {
  menu.value.show(event);
};
</script>
