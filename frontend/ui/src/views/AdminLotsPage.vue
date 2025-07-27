<template>
  <div>
    <h1>Manage Parking Lots</h1>
    <router-link to="/admin/dashboard">Back to Admin Dashboard</router-link>

    <hr />

    <h2>Create New Lot</h2>
    <form @submit.prevent="createLot">
      <div><label>Location Name:</label><input v-model="newLot.prime_location_name" type="text" required /></div>
      <div><label>Price (per hour):</label><input v-model="newLot.price" type="number" step="0.01" required /></div>
      <div><label>Address:</label><input v-model="newLot.address" type="text" required /></div>
      <div><label>Pin Code:</label><input v-model="newLot.pin_code" type="text" required /></div>
      <div><label>Number of Spots:</label><input v-model="newLot.number_of_spots" type="number" required /></div>
      <button type="submit">Create Lot</button>
    </form>
    <p v-if="message">{{ message }}</p>

    <hr />

    <h2>Existing Lots</h2>
    <div v-if="loading">Loading...</div>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Price</th>
          <th>Spots</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in lots" :key="lot.id">
          <td>{{ lot.id }}</td>
          <td><router-link :to="`/admin/lots/${lot.id}`">{{ lot.prime_location_name }}</router-link></td>
          <td>₹{{ lot.price.toFixed(2) }}</td>
          <td>{{ lot.number_of_spots }}</td>
          <td>
            <button @click="openEditModal(lot)">Edit</button>
            <button @click="deleteLot(lot.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editingLot" class="modal">
      <div class="modal-content">
        <span class="close" @click="editingLot = null">&times;</span>
        <h2>Edit Lot #{{ editingLot.id }}</h2>
        <form @submit.prevent="updateLot">
          <div><label>Location Name:</label><input v-model="editingLot.prime_location_name" type="text" required /></div>
          <div><label>Price (per hour):</label><input v-model="editingLot.price" type="number" step="0.01" required /></div>
          <div><label>Address:</label><input v-model="editingLot.address" type="text" required /></div>
          <div><label>Pin Code:</label><input v-model="editingLot.pin_code" type="text" required /></div>
          <button type="submit">Save Changes</button>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

const lots = ref([]);
const loading = ref(true);
const message = ref('');
const newLot = reactive({
  prime_location_name: '',
  price: 0,
  address: '',
  pin_code: '',
  number_of_spots: 0
});
const editingLot = ref(null);

const fetchLots = async () => {
  const token = localStorage.getItem('access_token');
  try {
    loading.value = true;
    const response = await axios.get('http://127.0.0.1:5000/api/lots', {
      headers: { Authorization: `Bearer ${token}` }
    });
    lots.value = response.data.lots;
  } catch (error) {
    console.error("Failed to fetch lots:", error);
    message.value = "Failed to load lots.";
  } finally {
    loading.value = false;
  }
};

const createLot = async () => {
  const token = localStorage.getItem('access_token');
  try {
    await axios.post('http://127.0.0.1:5000/api/lots', newLot, {
      headers: { Authorization: `Bearer ${token}` }
    });
    message.value = "Lot created successfully!";
    Object.assign(newLot, { prime_location_name: '', price: 0, address: '', pin_code: '', number_of_spots: 0 });
    await fetchLots();
  } catch (error) {
    console.error("Failed to create lot:", error);
    message.value = "Failed to create lot.";
  }
};

const deleteLot = async (lotId) => {
    if (!confirm("Are you sure you want to delete this lot and all its spots?")) return;

    const token = localStorage.getItem('access_token');
    try {
        await axios.delete(`http://127.0.0.1:5000/api/lots/${lotId}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        message.value = "Lot deleted successfully!";
        await fetchLots();
    } catch (error) {
        console.error("Failed to delete lot:", error);
        message.value = error.response?.data?.message || "Failed to delete lot.";
    }
};

const openEditModal = (lot) => {
  editingLot.value = { ...lot };
};

const updateLot = async () => {
  if (!editingLot.value) return;
  const token = localStorage.getItem('access_token');
  try {
    const updatePayload = {
        prime_location_name: editingLot.value.prime_location_name,
        price: editingLot.value.price,
        address: editingLot.value.address,
        pin_code: editingLot.value.pin_code,
    };
    await axios.put(`http://127.0.0.1:5000/api/lots/${editingLot.value.id}`, updatePayload, {
      headers: { Authorization: `Bearer ${token}` }
    });
    message.value = "Lot updated successfully!";
    editingLot.value = null;
    await fetchLots();
  } catch (error) {
    console.error("Failed to update lot:", error);
    message.value = "Failed to update lot.";
  }
};

onMounted(fetchLots);
</script>

<script>
export default {
  name: 'AdminLotsPage'
}
</script>

<style scoped>
  form div { margin-bottom: 10px; }
  label { margin-right: 10px; display: inline-block; width: 120px; }
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #f2f2f2; }
  hr { margin: 20px 0; }
  button { margin-right: 5px; }
  .modal { display: block; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); }
  .modal-content { background-color: #fefefe; margin: 15% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 500px; }
  .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; }
  .close:hover, .close:focus { color: black; text-decoration: none; cursor: pointer; }
</style>