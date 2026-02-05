import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import ManageDoctors from '../views/admin/ManageDoctors.vue'
import ManagePatients from '../views/admin/ManagePatients.vue'
import DoctorDashboard from '../views/doctor/DoctorDashboard.vue'
import PatientDashboard from '../views/patient/PatientDashboard.vue'
import BookAppointment from '../views/patient/BookAppointment.vue'
import MedicalHistory from '../views/patient/MedicalHistory.vue'
import Profile from '../views/patient/Profile.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  
  // Admin
  { path: '/admin', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/doctors', component: ManageDoctors, meta: { role: 'admin' } },
  { path: '/admin/patients', component: ManagePatients, meta: { role: 'admin' } },

  // Doctor
  { path: '/doctor', component: DoctorDashboard, meta: { role: 'doctor' } },

  // Patient
  { path: '/patient', component: PatientDashboard, meta: { role: 'patient' } },
  { path: '/patient/book', component: BookAppointment, meta: { role: 'patient' } },
  { path: '/patient/history', component: MedicalHistory, meta: { role: 'patient' } },
  { path: '/patient/profile', component: Profile, meta: { role: 'patient' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Simple Role Guard
router.beforeEach((to, from, next) => {
  const role = localStorage.getItem('role');
  if (to.meta.role && to.meta.role !== role) {
    return next('/login');
  }
  next();
});

export default router