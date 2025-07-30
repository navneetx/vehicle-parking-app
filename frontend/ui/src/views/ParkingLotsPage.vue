<template>
  <div class="lots-container">
    <div class="header">
      <h1>Available Parking Lots</h1>
      <router-link to="/dashboard" class="back-link">← Back to Dashboard</router-link>
    </div>

    <p v-if="message" class="message">{{ message }}</p>

    <div v-if="loading">Loading lots...</div>
    <table v-else class="lots-table">
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
          <td><button @click="bookSpot(lot.id)" class="btn-book">Book a Spot</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// --- State Management ---
const lots = ref([]);
const loading = ref(true);
const message = ref('');
const router = useRouter();

// --- API Functions ---
// Fetches the list of all available parking lots.
// This endpoint is cached on the backend for performance.
const fetchLots = async () => {
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
    message.value = "Could not load parking lots.";
  } finally {
    loading.value = false;
  }
};

// Sends a request to the backend to book a spot in a specific lot.
const bookSpot = async (lotId) => {
  const token = localStorage.getItem('access_token');
  message.value = 'Booking...'; // Provide immediate feedback to the user.
  try {
    const response = await axios.post('http://127.0.0.1:5000/api/user/reservations', 
      { lot_id: lotId }, // The data payload for the request
      { headers: { Authorization: `Bearer ${token}` } }
    );
    // Display a detailed success message from the API response.
    message.value = `${response.data.message} You got spot #${response.data.spot_number}.`;
  } catch (error) {
    // Display the specific error message from the backend (e.g., "already have a reservation").
    message.value = error.response?.data?.message || 'Failed to book spot.';
    console.error('Booking failed:', error);
  }
};

// --- Lifecycle Hook ---
onMounted(fetchLots);
</script>

<style scoped>
.lots-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.back-link {
  text-decoration: none;
  color: #007bff;
  font-weight: bold;
}
.lots-table {
  width: 100%;
  border-collapse: collapse;
}
.lots-table th, .lots-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
.lots-table th {
  background-color: #f8f9fa;
}
.btn-book {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  background-color: #28a745;
  color: white;
  cursor: pointer;
}
.btn-book:hover {
  background-color: #218838;
}
.message {
  margin-top: 15px;
  color: #0056b3;
  font-weight: bold;
}
</style>