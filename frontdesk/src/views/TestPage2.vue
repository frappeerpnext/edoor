<template>
  <div>
    <!-- Element to which you want to add a class -->
    <div @scroll="handleScroll()" id="ddd" :class="{ scrolled: isScrolled }">Scroll me!</div>
    <p>But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

    // Define a ref to track the scroll state
    const isScrolled = ref(false);

    // Function to handle the scroll event
    const handleScroll = (event) => {
      const v = document.querySelector('#ddd')
      
      // Check if the window has been scrolled
  if(window.scrollY > 60){
  }
      isScrolled.value = window.scrollY > 60;
    };

    // Add a scroll event listener when the component is mounted
    onMounted(() => {
      handleScroll();
    });

    // Remove the scroll event listener when the component is unmounted
    onBeforeUnmount(() => {
      window.removeEventListener('scroll', this.handleScroll);
    });

</script>

<style>
/* Define the style for the 'scrolled' class */
.scrolled {
  background-color: lightblue;
  /* Add any other styles you want to apply when scrolled */
}
</style>