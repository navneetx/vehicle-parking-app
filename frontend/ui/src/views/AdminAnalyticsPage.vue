<template>
  <div class="analytics-container">
    <div class="header">
      <h1>Parking Analytics</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Admin Dashboard</router-link>
    </div>

    <div class="chart-card">
      <h2>Revenue per Parking Lot</h2>
      <div v-if="loading">Loading chart data...</div>
      <!-- The Bar component from vue-chartjs renders the chart -->
      <Bar v-else :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

// --- Chart.js Registration ---
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

// --- State Management ---
const loading = ref(true);
// This holds the data for the chart in the specific format Chart.js requires.
const chartData = ref({
  labels: [],
  datasets: [{
    label: 'Total Revenue (₹)',
    backgroundColor: '#4CAF50',
    data: []
  }]
});
// This holds the configuration options for the chart's appearance and behavior.
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false
});

// --- Lifecycle Hook ---
onMounted(async () => {
  const token = localStorage.getItem('access_token');
  try {
    // Fetch the revenue summary data from the backend API.
    const response = await axios.get('http://127.0.0.1:5000/api/admin/revenue', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    const revenueSummary = response.data.revenue_summary;
    
    // --- Data Transformation ---
    // The API data needs to be transformed into separate arrays for labels and data points.
    const labels = revenueSummary.map(item => item.lot_name);
    const dataPoints = revenueSummary.map(item => item.total_revenue);
    
    // Update the reactive chartData object, which will cause the chart to render.
    chartData.value = {
      labels: labels,
      datasets: [{
        label: 'Total Revenue (₹)',
        backgroundColor: '#4CAF50',
        data: dataPoints
      }]
    };
    
  } catch (error) {
    console.error("Failed to fetch analytics data:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.analytics-container {
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
.chart-card {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  /* This height is required by vue-chartjs when maintainAspectRatio is false */
  height: 60vh; 
}
h2 {
  text-align: center;
  margin-top: 0;
}
</style>