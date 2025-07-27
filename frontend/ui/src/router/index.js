import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import DashboardPage from '../views/DashboardPage.vue';
import ParkingLotsPage from '../views/ParkingLotsPage.vue';
import AdminDashboardPage from '../views/AdminDashboardPage.vue';
import AdminLotsPage from '../views/AdminLotsPage.vue';
import AdminUsersPage from '../views/AdminUsersPage.vue';
import AdminLotDetailsPage from '../views/AdminLotDetailsPage.vue';
import AdminAnalyticsPage from '../views/AdminAnalyticsPage.vue';

const routes = [
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/register', name: 'Register', component: RegisterPage },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/lots',
    name: 'ParkingLots',
    component: ParkingLotsPage,
    meta: { requiresAuth: true }
  },
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

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('access_token');
  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router;