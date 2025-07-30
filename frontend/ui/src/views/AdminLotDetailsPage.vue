<template>
  <div class="details-container">
    <div class="header">
      <h1>Lot Details: {{ lot.prime_location_name || 'Loading...' }}</h1>
      <router-link to="/admin/lots" class="back-link">← Back to All Lots</router-link>
    </div>

    <div v-if="loading">Loading spot details...</div>
    <div v-else class="details-card">
      <h3>All Spots ({{ lot.spots ? lot.spots.length : 0 }} Total)</h3>
      <ul class="spot-grid">
        <!-- Loop through each spot and display its status -->
        <li v-for="spot in lot.spots" :key="spot.id" :class="spot.status" class="spot-item">
          <strong>Spot #{{ spot.spot_number }}</strong>
          <span>{{ spot.status }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

// --- State Management ---
const lot = ref({});
const loading = ref(true);
// `useRoute` is a Vue Router hook to access information about the current route.
const route = useRoute();

// --- Lifecycle Hook ---
onMounted(async () => {
  // Get the dynamic 'id' parameter from the URL (e.g., the '1' in /admin/lots/1).
  const lotId = route.params.id;
  const token = localStorage.getItem('access_token');
  
  try {
    // Fetch the details for this specific lot from the backend.
    const response = await axios.get(`http://127.0.0.1:5000/api/lots/${lotId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    lot.value = response.data;
  } catch (error) {
    console.error("Failed to fetch lot details:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.details-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 30px;
}
.back-link {
  text-decoration: none;
  color: #007bff;
  font-weight: bold;
}
.details-card {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.spot-grid {
  list-style-type: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}
.spot-item {
  border: 1px solid #ccc;
  padding: 15px;
  border-radius: 5px;
  text-align: center;
  font-weight: bold;
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-transform: capitalize;
}
/* Conditional styling based on the spot's status */
.spot-item.available {
  background-color: #d4edda; /* Green */
  border-color: #c3e6cb;
  color: #155724;
}
.spot-item.occupied {
  background-color: #f8d7da; /* Red */
  border-color: #f5c6cb;
  color: #721c24;
}
</style>