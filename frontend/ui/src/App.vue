<template>
  <div id="app">
    <AppNavbar />
    <div class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import AppNavbar from './components/AppNavbar.vue';

export default {
  name: 'App',
  components: {
    AppNavbar
  }
}
</script>

<style>
.container {
  padding: 0 20px;
}
</style>