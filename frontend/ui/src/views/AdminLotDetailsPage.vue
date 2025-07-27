<template>
  <div>
    <h1>Lot Details: {{ lot.prime_location_name }}</h1>
    <router-link to="/admin/lots">Back to All Lots</router-link>

    <div v-if="loading">Loading details...</div>
    <div v-else>
      <h3>All Spots</h3>
      <ul class="spot-list">
        <li v-for="spot in lot.spots" :key="spot.id" :class="spot.status">
          Spot #{{ spot.spot_number }} (Status: {{ spot.status }})
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const lot = ref({});
const loading = ref(true);
const route = useRoute();

onMounted(async () => {
  const lotId = route.params.id;
  const token = localStorage.getItem('access_token');
  try {
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

<script>
export default {
  name: 'AdminLotDetailsPage'
}
</script>

<style scoped>
  .spot-list {
    list-style-type: none;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  .spot-list li {
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
    width: 150px;
    text-align: center;
  }
  .spot-list li.available {
    background-color: #d4edda; /* Green */
    border-color: #c3e6cb;
  }
  .spot-list li.occupied {
    background-color: #f8d7da; /* Red */
    border-color: #f5c6cb;
  }
</style>