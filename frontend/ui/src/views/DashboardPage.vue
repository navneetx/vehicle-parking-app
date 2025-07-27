<template>
  <div>
    <h1>Welcome to Your Dashboard!</h1>
    <button @click="logout">Logout</button>

    <div class="nav-link">
      <router-link to="/lots">View & Book Parking Lots</router-link>
    </div>

    <div class="export-section">
      <button @click="triggerExport">Export History to CSV</button>
      <p v-if="exportMessage">{{ exportMessage }}</p>
    </div>

    <div v-if="activeReservation" class="active-reservation">
      <h2>Current Parking Status</h2>
      <p>
        You are currently parked at <strong>{{ activeReservation.lot_name }}</strong> in spot
        <strong>#{{ activeReservation.spot_number }}</strong>.
      </p>
      <p>Parked at: {{ formatDateTime(activeReservation.parking_time) }}</p>
      <button @click="releaseSpot">Release My Spot</button>
      <p v-if="releaseMessage">{{ releaseMessage }}</p>
    </div>

    <h2>Your Parking History</h2>
    <div v-if="loading">Loading history...</div>
    <div v-else-if="history.length === 0">No parking history found.</div>
    <table v-else>
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

const history = ref([]);
const activeReservation = ref(null);
const loading = ref(true);
const releaseMessage = ref('');
const exportMessage = ref('');
const router = useRouter();

const formatDateTime = (isoString) => {
  if (!isoString) return '';
  return formatInTimeZone(new Date(isoString), 'Asia/Kolkata', 'dd/MM/yyyy, hh:mm:ss a');
};

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
    activeReservation.value = history.value.find(rec => rec.leaving_time === null) || null;
  } catch (error) {
    console.error('Failed to fetch history:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchHistory);

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
  router.push('/login');
};

const releaseSpot = async () => {
  const token = localStorage.getItem('access_token');
  try {
    const response = await axios.put('http://127.0.0.1:5000/api/user/reservations/active', {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    releaseMessage.value = response.data.message;
    await fetchHistory();
  } catch (error) {
    releaseMessage.value = error.response?.data?.message || 'Failed to release spot.';
    console.error('Failed to release spot:', error);
  }
};

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
</script>

<style scoped>
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }
  th {
    background-color: #f2f2f2;
  }
  button, .nav-link {
    margin-bottom: 20px;
  }
  .active-reservation {
    border: 1px solid #4CAF50;
    background-color: #f0fff0;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
  }
  .export-section {
    margin-top: 20px;
    margin-bottom: 20px;
    padding: 15px;
    background-color: #e7f3fe;
    border-left: 6px solid #2196F3;
  }
</style>