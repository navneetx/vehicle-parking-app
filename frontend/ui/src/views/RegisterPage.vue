<template>
  <div class="register-container">
    <h1>Register</h1>
    <form @submit.prevent="handleRegister" class="register-form">
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" type="text" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" type="password" v-model="password" required />
      </div>
      <button type="submit">Register</button>
      <p v-if="message" class="message">{{ message }}</p>
    </form>
    <p>Already have an account? <router-link to="/login">Login here</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// Reactive variables for form input and user feedback.
const username = ref('');
const password = ref('');
const message = ref('');
const router = useRouter();

// This function is called when the registration form is submitted.
const handleRegister = async () => {
  try {
    // Send the new user's credentials to the backend registration endpoint.
    await axios.post('http://127.0.0.1:5000/auth/register', {
      username: username.value,
      password: password.value
    });

    // If registration is successful, automatically redirect the user to the login page.
    router.push('/login');

  } catch (error) {
    // Handle potential errors from the API.
    // Specifically check for a 409 Conflict error, which means the username is already taken.
    if (error.response && error.response.status === 409) {
      message.value = 'Username already exists. Please choose another.';
    } else {
      message.value = 'An error occurred during registration.';
    }
    console.error('Registration failed:', error);
  }
};
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  text-align: center;
}
.register-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.form-group {
  text-align: left;
}
label {
  display: block;
  margin-bottom: 5px;
}
input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  padding: 10px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background-color: #1e88e5;
}
.message {
  color: red;
  margin-top: 10px;
}
</style>