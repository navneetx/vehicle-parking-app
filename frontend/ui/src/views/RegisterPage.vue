<template>
  <div>
    <h1>Register</h1>
    <form @submit.prevent="handleRegister">
      <div>
        <label>Username</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label>Password</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Register</button>
      <p v-if="message">{{ message }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const message = ref(''); // To show success or error messages
const router = useRouter();

const handleRegister = async () => {
  try {
    // Send a POST request to the backend register endpoint
    await axios.post('http://127.0.0.1:5000/auth/register', {
      username: username.value,
      password: password.value
    });

    // If registration is successful, redirect to the login page
    router.push('/login');

  } catch (error) {
    // If there's an error (e.g., username already exists), display a message
    if (error.response && error.response.status === 409) {
      message.value = 'Username already exists. Please choose another.';
    } else {
      message.value = 'An error occurred during registration.';
    }
    console.error('Registration failed:', error);
  }
};
</script>

<script>
export default {
  name: 'RegisterPage'
}
</script>