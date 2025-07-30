import { createRouter, createWebHistory } from 'vue-router';

// --- Page Component Imports ---
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import DashboardPage from '../views/DashboardPage.vue';
import ParkingLotsPage from '../views/ParkingLotsPage.vue';
import AdminDashboardPage from '../views/AdminDashboardPage.vue';
import AdminLotsPage from '../views/AdminLotsPage.vue';
import AdminUsersPage from '../views/AdminUsersPage.vue';
import AdminLotDetailsPage from '../views/AdminLotDetailsPage.vue';
import AdminAnalyticsPage from '../views/AdminAnalyticsPage.vue';

// --- Route Definitions ---
// This array maps URL paths to their corresponding Vue components.
const routes = [
  // Public routes
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/register', name: 'Register', component: RegisterPage },
  
  // User-specific routes
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true } // This meta field marks the route as protected.
  },
  {
    path: '/lots',
    name: 'ParkingLots',
    component: ParkingLotsPage,
    meta: { requiresAuth: true }
  },
  
  // Admin-specific routes
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/lots',
    name: 'AdminLots',
    component: AdminLotsPage,
    meta: { requiresAuth: true }
  },
  {
    // This is a dynamic route. The `:id` part is a parameter that can change.
    // For example, it will match /admin/lots/1, /admin/lots/2, etc.
    path: '/admin/lots/:id',
    name: 'AdminLotDetails',
    component: AdminLotDetailsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsersPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/analytics',
    name: 'AdminAnalytics',
    component: AdminAnalyticsPage,
    meta: { requiresAuth: true }
  }
];

// --- Router Instance Creation ---
const router = createRouter({
  history: createWebHistory(), // Uses the browser's history API for clean URLs.
  routes
});

// --- Global Navigation Guard ---
// This function runs before every single navigation request.
// It's the core of the frontend authentication check.
router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('access_token');

  // Check if the route the user is trying to access has `meta.requiresAuth`.
  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    // If the route is protected and the user is not logged in,
    // redirect them to the login page.
    next('/login');
  } else {
    // Otherwise, allow the navigation to proceed.
    next();
  }
});

export default router;