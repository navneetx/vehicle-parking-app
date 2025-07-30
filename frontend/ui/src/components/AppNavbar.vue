<template>
  <!-- This now checks our new 'showNavbar' logic -->
  <nav class="navbar" v-if="showNavbar">
    <div>
      <span>Logged in as: <strong>{{ userRole }}</strong></span>
    </div>
    <div>
      <button @click="logout">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, watch, computed } from 'vue'; // <-- Import 'computed'
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = ref(!!localStorage.getItem('access_token'));
const userRole = ref(localStorage.getItem('user_role') || '');

// This is our new logic. It's a "computed property" that automatically
// updates when other values (like the current route) change.
const showNavbar = computed(() => {
  const routeName = router.currentRoute.value.name;
  // Only show the navbar if the user is logged in AND not on the Login or Register page.
  return isLoggedIn.value && routeName !== 'Login' && routeName !== 'Register';
});

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
  isLoggedIn.value = false;
  userRole.value = '';
  router.push('/login');
};

// Watch for route changes to update the logged-in status
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