<template>
  <div class="manage-lots-container">
    <div class="header">
      <h1>Manage Parking Lots</h1>
      <router-link to="/admin/dashboard" class="back-link">← Back to Admin Dashboard</router-link>
    </div>

    <div class="content-layout">
      <!-- Left Side: Form to Create New Lot -->
      <div class="form-card">
        <h2>Create New Lot</h2>
        <form @submit.prevent="createLot" class="lot-form">
          <div class="form-group">
            <label>Location Name:</label>
            <input v-model="newLot.prime_location_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Price (per hour):</label>
            <input v-model="newLot.price" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Address:</label>
            <input v-model="newLot.address" type="text" required />
          </div>
          <div class="form-group">
            <label>Pin Code:</label>
            <input v-model="newLot.pin_code" type="text" required />
          </div>
          <div class="form-group">
            <label>Number of Spots:</label>
            <input v-model="newLot.number_of_spots" type="number" required />
          </div>
          <button type="submit" class="btn-create">Create Lot</button>
        </form>
        <p v-if="message" class="message">{{ message }}</p>
      </div>

      <!-- Right Side: Table of Existing Lots -->
      <div class="table-card">
        <h2>Existing Lots</h2>
        <div v-if="loading">Loading...</div>
        <table v-else class="lots-table">
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
              <td class="actions">
                <button @click="openEditModal(lot)" class="btn-edit">Edit</button>
                <button @click="deleteLot(lot.id)" class="btn-delete">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Lot Modal (Pop-up) -->
    <div v-if="editingLot" class="modal-overlay">
      <div class="modal-content">
        <span class="close-button" @click="editingLot = null">&times;</span>
        <h2>Edit Lot #{{ editingLot.id }}</h2>
        <form @submit.prevent="updateLot" class="lot-form">
          <div class="form-group"><label>Location Name:</label><input v-model="editingLot.prime_location_name" type="text" required /></div>
          <div class="form-group"><label>Price (per hour):</label><input v-model="editingLot.price" type="number" step="0.01" required /></div>
          <div class="form-group"><label>Address:</label><input v-model="editingLot.address" type="text" required /></div>
          <div class="form-group"><label>Pin Code:</label><input v-model="editingLot.pin_code" type="text" required /></div>
          <button type="submit" class="btn-create">Save Changes</button>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

// --- State Management ---
// Reactive variables for the component's data.
const lots = ref([]);
const loading = ref(true);
const message = ref('');
// `reactive` is used for objects, `ref` for primitives or when reassigning the whole object.
const newLot = reactive({
  prime_location_name: '',
  price: 0,
  address: '',
  pin_code: '',
  number_of_spots: 0
});
// This holds the lot object when the edit modal is open. `null` means the modal is closed.
const editingLot = ref(null);

// --- API Functions (CRUD Operations) ---
// Fetches all parking lots from the backend.
const fetchLots = async () => {
  const token = localStorage.getItem('access_token');
  try {
    loading.value = true;
    const response = await axios.get('http://127.0.0.1:5000/api/lots', {
      headers: { Authorization: `Bearer ${token}` }
    });
    lots.value = response.data.lots;
  } catch (error) {
    message.value = "Failed to load lots.";
  } finally {
    loading.value = false;
  }
};

// Creates a new parking lot.
const createLot = async () => {
  const token = localStorage.getItem('access_token');
  try {
    await axios.post('http://127.0.0.1:5000/api/lots', newLot, {
      headers: { Authorization: `Bearer ${token}` }
    });
    message.value = "Lot created successfully!";
    // Reset the form fields after successful creation.
    Object.assign(newLot, { prime_location_name: '', price: 0, address: '', pin_code: '', number_of_spots: 0 });
    await fetchLots(); // Refresh the list of lots to show the new one.
  } catch (error) {
    message.value = "Failed to create lot.";
  }
};

// Deletes a parking lot by its ID.
const deleteLot = async (lotId) => {
    if (!confirm("Are you sure you want to delete this lot and all its spots?")) return;
    
    const token = localStorage.getItem('access_token');
    try {
        await axios.delete(`http://127.0.0.1:5000/api/lots/${lotId}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        message.value = "Lot deleted successfully!";
        await fetchLots(); // Refresh the list.
    } catch (error) {
        message.value = error.response?.data?.message || "Failed to delete lot.";
    }
};

// Opens the edit modal by setting the `editingLot` state variable.
const openEditModal = (lot) => {
  // Create a copy of the lot object to avoid changing the table data while editing.
  editingLot.value = { ...lot };
};

// Updates an existing parking lot.
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
    editingLot.value = null; // Close the modal on success.
    await fetchLots(); // Refresh the list.
  } catch (error) {
    message.value = "Failed to update lot.";
  }
};

// --- Lifecycle Hook ---
// `onMounted` is a Vue lifecycle hook that runs automatically when the component
// is first loaded. It's the standard place to make initial API calls.
onMounted(fetchLots);
</script>

<style scoped>
.manage-lots-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}
.back-link {
  text-decoration: none;
  color: #007bff;
  font-weight: bold;
}
.content-layout {
  display: flex;
  gap: 30px;
  margin-top: 20px;
}
.form-card {
  flex: 1;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}
.table-card {
  flex: 2;
}
.lot-form .form-group {
  margin-bottom: 15px;
}
.lot-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.lot-form input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
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
  background-color: #f2f2f2;
}
.lots-table .actions {
  display: flex;
  gap: 5px;
}
.message {
  margin-top: 15px;
  color: #0056b3;
}
button {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}
.btn-create { background-color: #28a745; }
.btn-edit { background-color: #ffc107; color: #333; }
.btn-delete { background-color: #dc3545; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  z-index: 100;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  position: relative;
}
.close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  color: #aaa;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}
</style>