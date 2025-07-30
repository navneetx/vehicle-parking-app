<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" type="text" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
    <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// Reactive variables to store form input and messages.
const username = ref('');
const password = ref('');
const errorMessage = ref('');
const router = useRouter();

// This function is called when the login form is submitted.
const handleLogin = async () => {
  // First, clear any existing login data from the browser's storage.
  // This prevents conflicts if a different user was previously logged in.
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');

  try {
    // Step 1: Send the username and password to the backend login endpoint.
    const loginResponse = await axios.post('http://127.0.0.1:5000/auth/login', {
      username: username.value,
      password: password.value
    });

    // On success, the backend returns a JWT access token.
    const token = loginResponse.data.access_token;
    localStorage.setItem('access_token', token);

    // Step 2: Use the new token to get the user's profile information (especially their role).
    const profileResponse = await axios.get('http://127.0.0.1:5000/auth/profile', {
        headers: { Authorization: `Bearer ${token}` }
    });

    const userRole = profileResponse.data.role;
    localStorage.setItem('user_role', userRole);

    // Step 3: Redirect the user to the correct dashboard based on their role.
    if (userRole === 'admin') {
        router.push('/admin/dashboard');
    } else {
        router.push('/dashboard');
    }

  } catch (error) {
    // If any API call fails, show an error message to the user.
    errorMessage.value = 'Invalid credentials. Please try again.';
    console.error('Login failed:', error);
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  text-align: center;
}
.login-form {
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
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background-color: #45a049;
}
.error-message {
  color: red;
  margin-top: 10px;
}
</style>