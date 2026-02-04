import { createRouter, createWebHistory } from 'vue-router';

// Lazy-loaded route components
const Login = () => import('../views/auth/Login.vue');
const Register = () => import('../views/auth/Register.vue');

// Admin Views
const AdminDashboard = () => import('../views/admin/AdminDashboard.vue');
const ManageDoctors = () => import('../views/admin/ManageDoctors.vue');
const ManagePatients = () => import('../views/admin/ManagePatients.vue');

// Doctor Views
const DoctorDashboard = () => import('../views/doctor/DoctorDashboard.vue');
//const DoctorSchedule = () => import('../views/doctor/DoctorSchedule.vue');

// Patient Views
const PatientDashboard = () => import('../views/patient/PatientDashboard.vue');
const BookAppointment = () => import('../views/patient/BookAppointment.vue');
const MedicalHistory = () => import('../views/patient/MedicalHistory.vue');

// System Views
const NotFound = { template: '<div>404 Not Found</div>' };

const routes = [
  // Authentication
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },

  // Admin Routes
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { auth: true, role: 'admin' }
  },
  {
    path: '/admin/doctors',
    name: 'ManageDoctors',
    component: ManageDoctors,
    meta: { auth: true, role: 'admin' }
  },
  {
    path: '/admin/patients',
    name: 'ManagePatients',
    component: ManagePatients,
    meta: { auth: true, role: 'admin' }
  },

  // Doctor Routes
  {
    path: '/doctor/dashboard',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { auth: true, role: 'doctor' }
  },
  /*{
    path: '/doctor/schedule',
    name: 'DoctorSchedule',
    component: DoctorSchedule,
    meta: { auth: true, role: 'doctor' }
  },*/

  // Patient Routes
  {
    path: '/patient/dashboard',
    name: 'PatientDashboard',
    component: PatientDashboard,
    meta: { auth: true, role: 'patient' }
  },
  {
    path: '/patient/book',
    name: 'BookAppointment',
    component: BookAppointment,
    meta: { auth: true, role: 'patient' }
  },
  {
    path: '/patient/history',
    name: 'MedicalHistory',
    component: MedicalHistory,
    meta: { auth: true, role: 'patient' }
  },

  // Root Redirect
  {
    path: '/',
    name: 'Root',
    redirect: () => {
      const role = localStorage.getItem('user_role');
      const allowedRoles = ['admin', 'doctor', 'patient'];

      if (allowedRoles.includes(role)) {
        return `/${role}/dashboard`;
      }
      return '/login';
    }
  },

  // Catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation Guards
router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem('user_role');
  const isLoggedIn = !!userRole;
  const allowedRoles = ['admin', 'doctor', 'patient'];

  // 1️⃣ Auth required but user not logged in
  if (to.meta.auth && !isLoggedIn) {
    return next('/login');
  }

  // 2️⃣ Guest-only routes (login/register)
  if (to.meta.guest && isLoggedIn) {
    if (allowedRoles.includes(userRole)) {
      return next(`/${userRole}/dashboard`);
    }
    return next('/login');
  }

  // 3️⃣ Role-based authorization
  if (to.meta.role) {
    if (!allowedRoles.includes(userRole)) {
      return next('/login');
    }

    if (userRole !== to.meta.role) {
      return next(`/${userRole}/dashboard`);
    }
  }

  next();
});

export default router;