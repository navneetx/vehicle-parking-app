<template>
  <nav class="navbar" v-if="isLoggedIn">
    <div>
      <span>Logged in as: <strong>{{ userRole }}</strong></span>
    </div>
    <div>
      <button @click="logout">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(!!localStorage.getItem('access_token'));
const userRole = ref(localStorage.getItem('user_role') || '');

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
  isLoggedIn.value = false;
  userRole.value = '';
  router.push('/login');
};

// Watch for route changes to update the navbar's state
watch(() => router.currentRoute.value, () => {
  isLoggedIn.value = !!localStorage.getItem('access_token');
  userRole.value = localStorage.getItem('user_role') || '';
});
</script>

<style scoped>
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f2f2f2;
    padding: 10px 20px;
    margin-bottom: 20px;
    border-radius: 5px;
  }
</style>