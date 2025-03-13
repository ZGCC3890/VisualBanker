<template>
  <!-- <div id="app"> -->
    <!-- <h1>银行家算法可视化</h1> -->
    <Banker />
  <!-- </div> -->
</template>

<script>
import Banker from "./components/Banker.vue";

export default {
  components: {
    Banker,
  },
};
</script>

<style>
#app {
  text-align: center;
  font-family: Arial, sans-serif;
  margin-top: 20px;
}
</style>
