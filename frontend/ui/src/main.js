import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // Import our new router

createApp(App).use(router).mount('#app'); // Tell the app to use it