<template>
  <div class="dashboard-container">
    <h1>Welcome to Your Dashboard</h1>
    
    <div class="actions-container">
      <router-link to="/lots" class="action-button">View & Book Parking Lots</router-link>
      <button @click="triggerExport" class="action-button">Export History to CSV</button>
    </div>
    <p v-if="exportMessage" class="message">{{ exportMessage }}</p>

    <!-- This section only appears if there's an active reservation -->
    <div v-if="activeReservation" class="active-reservation">
      <h2>Current Parking Status</h2>
      <p>
        You are currently parked at <strong>{{ activeReservation.lot_name }}</strong> in spot
        <strong>#{{ activeReservation.spot_number }}</strong>.
      </p>
      <p>Parked at: {{ formatDateTime(activeReservation.parking_time) }}</p>
      <button @click="releaseSpot">Release My Spot</button>
      <p v-if="releaseMessage" class="message">{{ releaseMessage }}</p>
    </div>

    <h2>Your Parking History</h2>
    <div v-if="loading">Loading history...</div>
    <div v-else-if="history.length === 0">No parking history found.</div>
    <table v-else class="history-table">
      <thead>
        <tr>
          <th>Lot Name</th>
          <th>Spot Number</th>
          <th>Parking Time</th>
          <th>Leaving Time</th>
          <th>Cost</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in history" :key="item.reservation_id">
          <td>{{ item.lot_name }}</td>
          <td>{{ item.spot_number }}</td>
          <td>{{ formatDateTime(item.parking_time) }}</td>
          <td>{{ item.leaving_time ? formatDateTime(item.leaving_time) : 'Currently Parked' }}</td>
          <td>{{ item.cost !== null ? '₹' + item.cost.toFixed(2) : 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { formatInTimeZone } from 'date-fns-tz';

// --- State Management ---
// Reactive variables to hold the component's state.
const history = ref([]);
const activeReservation = ref(null);
const loading = ref(true);
const releaseMessage = ref('');
const exportMessage = ref('');
const router = useRouter();

// --- Helper Functions ---
// A utility function to format UTC date strings into a readable local format.
const formatDateTime = (isoString) => {
  if (!isoString) return '';
  return formatInTimeZone(new Date(isoString), 'Asia/Kolkata', 'dd/MM/yyyy, hh:mm:ss a');
};

// --- API Calls ---
// Fetches the user's complete parking history from the backend.
const fetchHistory = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    router.push('/login');
    return;
  }

  try {
    loading.value = true;
    const response = await axios.get('http://127.0.0.1:5000/api/user/reservations', {
      headers: { Authorization: `Bearer ${token}` }
    });
    history.value = response.data.history;
    // After fetching, check if any record is active (has no leaving_time).
    activeReservation.value = history.value.find(rec => rec.leaving_time === null) || null;
  } catch (error) {
    console.error('Failed to fetch history:', error);
  } finally {
    loading.value = false;
  }
};

// Ends the user's active parking session.
const releaseSpot = async () => {
  const token = localStorage.getItem('access_token');
  try {
    const response = await axios.put('http://127.0.0.1:5000/api/user/reservations/active', {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    releaseMessage.value = response.data.message;
    await fetchHistory(); // Refresh the history to show the changes.
  } catch (error) {
    releaseMessage.value = error.response?.data?.message || 'Failed to release spot.';
    console.error('Failed to release spot:', error);
  }
};

// Triggers the background job to generate a CSV export.
const triggerExport = async () => {
  const token = localStorage.getItem('access_token');
  try {
    exportMessage.value = 'Starting export... The CSV file will be saved in the backend/exports folder.';
    const response = await axios.post('http://127.0.0.1:5000/api/user/export-csv', {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    exportMessage.value = response.data.message;
  } catch (error) {
    exportMessage.value = 'Failed to start export.';
    console.error('Export failed:', error);
  }
};

// --- Lifecycle Hooks ---
// The `onMounted` hook runs automatically as soon as the component is added to the page.
onMounted(fetchHistory);

</script>

<style scoped>
.dashboard-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
}
.actions-container {
  display: flex;
  gap: 15px;
  margin: 20px 0;
}
.action-button {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  cursor: pointer;
  font-size: 1em;
}
.action-button:hover {
  background-color: #0056b3;
}
.message {
  margin-top: 10px;
  color: #0056b3;
}
.active-reservation {
  border: 1px solid #28a745;
  background-color: #d4edda;
  padding: 15px;
  margin: 20px 0;
  border-radius: 5px;
}
.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
.history-table th, .history-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
.history-table th {
  background-color: #f8f9fa;
}
</style>