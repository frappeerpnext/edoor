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
      {{ room.room_number }} {{ room.width }}, {{ room.height }}
    </template>
  </div>

  <ContextMenu ref="menu" :model="contextMenuItems" />

  <OverlayPanel
    ref="op"
    class="style_penal bg-white p-4 rounded-lg shadow-lg max-w-md w-full"
  >
    <InputText type="text" v-model="elementStyle.elementText" />
    
    <p>
      Texttranform:
      <ComSelect v-model="elementStyle.textTranform" :options="['none','lowercase']"/>
    </p>

    <p>
      Text Effect:
      <ComSelect v-model="elementStyle.textEffect" :options="['none','rotate']"/>
    </p>
    <p>
      Rotate Degree
      <Slider
      v-model="elementStyle.rotateDegree"
      :min="0"
      :max="360"
      class="w-56"
        v-if="elementStyle.textEffect === 'rotate'"
      />
    </p>

    <p>
      font size
      <Slider
        v-model="elementStyle.fontSize"
        :min="10"
        :max="30"
        class="w-56"
      />
    </p>
    <p>
      TextColor:
      <ColorPicker v-model="elementStyle.color" />
    </p>
    <p>
      BackgroundColor :

      <ColorPicker v-model="elementStyle.background" />
    </p>
    <p>
      BorderColor :

      <ColorPicker v-model="elementStyle.borderColor" />
      <p class="my-2">
        
        <Slider
          v-model="elementStyle.borderWidth"
          :min="1"
          :max="10"
          class="w-56"
        />
      </p>

      <ComSelect
        v-model="elementStyle.justifyContent"
        :options="['left', 'center', 'right', 'start', 'end']"
      />
      <ComSelect
        v-model="elementStyle.alignItems"
        :options="['start', 'center', 'end']"
      />
    </p>
  </OverlayPanel>
</template>
<script setup>
import { ref, inject, watch, h } from "@/plugin";
import { i18n } from "@/i18n";
import ContextMenu from "primevue/contextmenu";
import ComElementTooltip from "@/views/floor_plan_view/components/ComElementTooltip.vue";
import { useTippy } from "vue-tippy";
import ColorPicker from "primevue/colorpicker";
import Slider from "primevue/slider";

const op = ref();
const emit = defineEmits(["onDelete"]);
const { t: $t } = i18n.global;

const props = defineProps({
  room: Object,
});

const menu = ref();
const elementStyle = ref({
  color: "000",
  background: "fff",
  borderColor: "000",
  justifyContent: "center",
  fontSize: "10",
  alignItems: "center",
  borderWidth: 1,
  rotateDegree:0,
  textEffect:"none",
  textTranform:"none"
});
const elementText = ref("");
let element = null;

const toggle = (event) => {
  element = document
    .querySelector(".drv-active")
    .querySelector(".floor-plan-element")
    .querySelector("div");
  if (element) {
    const computedStyles = window.getComputedStyle(element);

    Object.keys(elementStyle.value).forEach((key) => {
      if (key == "color" || key == "background" || key == "borderColor") {
        elementStyle.value[key] = computedStyles[key].replace("#", "");
      } else if (key == "borderWidth" || key == "fontSize") {
        elementStyle.value[key] = computedStyles[key].replace("px", "");
      }else {
        if (key != "elementText") elementStyle.value[key] = computedStyles[key];
      }
      
    });
    elementStyle.value.elementText = element.textContent;
    op.value.toggle(event);
  }
};
const contextMenuItems = ref([
  {
    label: $t("Send to Back"),
    icon: "pi pi-copy",
    command: function () {
      if ((props.room.z_index || 0) > 0) {
        props.room.z_index = (props.room.z_index || 0) - 1;
      }
    },
  },
  {
    label: $t("Bring to Front"),
    icon: "pi pi-copy",
    command: function () {
      props.room.z_index = (props.room.z_index || 0) + 1;
    },
  },
]);

if (props.room.element) {
  contextMenuItems.value.push({
    label: $t("Delete"),
    icon: "pi pi-copy",
    command: function () {
      props.room.is_deleted = 1;
    },
  });
}

watch(elementStyle.value, (newValue, oldValue) => {
  if (element) {
    Object.keys(elementStyle.value).forEach((key) => {
      if (key == "color" || key == "background" || key == "borderColor") {
        element.style[key] = `#${elementStyle.value[key]}`;
      } else if (key == "borderWidth" || key == "fontSize") {
        element.style[key] = `${elementStyle.value[key]}px`;
      } else {
        if (key == "elementText") {
          element.textContent = elementStyle.value[key];
        } else {
          element.style[key] = elementStyle.value[key];
        }
      }
    });
    props.room.element = element.outerHTML;
  }
});

const onOpenMenu = (event) => {
  menu.value.show(event);
};
</script>
