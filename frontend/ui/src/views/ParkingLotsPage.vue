<template>
  <div>
    <h1>Available Parking Lots</h1>
    <router-link to="/dashboard">Back to Dashboard</router-link>
    <p v-if="message">{{ message }}</p>

    <div v-if="loading">Loading lots...</div>
    <table v-else>
      <thead>
        <tr>
          <th>Location</th>
          <th>Address</th>
          <th>Price (per hour)</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in lots" :key="lot.id">
          <td>{{ lot.prime_location_name }}</td>
          <td>{{ lot.address }}</td>
          <td>₹{{ lot.price.toFixed(2) }}</td>
          <td><button @click="bookSpot(lot.id)">Book a Spot</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const lots = ref([]);
const loading = ref(true);
const message = ref('');
const router = useRouter();

onMounted(async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    router.push('/login');
    return;
  }

  try {
    const response = await axios.get('http://127.0.0.1:5000/api/user/lots', {
      headers: { Authorization: `Bearer ${token}` }
    });
    lots.value = response.data.lots;
  } catch (error) {
    console.error('Failed to fetch lots:', error);
  } finally {
    loading.value = false;
  }
});

const bookSpot = async (lotId) => {
  const token = localStorage.getItem('access_token');
  message.value = 'Booking...';
  try {
    const response = await axios.post('http://127.0.0.1:5000/api/user/reservations', 
      { lot_id: lotId },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    message.value = `${response.data.message} You got spot #${response.data.spot_number}.`;
  } catch (error) {
    message.value = error.response.data.message || 'Failed to book spot.';
    console.error('Booking failed:', error);
  }
};
</script>

<script>
export default {
  name: 'ParkingLotsPage'
}
</script>

<style scoped>
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #f2f2f2; }
  button { margin-bottom: 0; }
  p { margin-top: 10px; }
</style>