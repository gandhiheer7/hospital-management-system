<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">HMS V2</router-link>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="userRole">
          
          <template v-if="userRole === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/doctors">Doctors</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/patients">Patients</router-link>
            </li>
          </template>

          <template v-if="userRole === 'doctor'">
            <li class="nav-item">
              <router-link class="nav-link" to="/doctor/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/doctor/schedule">Schedule</router-link>
            </li>
          </template>

          <template v-if="userRole === 'patient'">
            <li class="nav-item">
              <router-link class="nav-link" to="/patient/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/patient/book">Book Appointment</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/patient/history">Medical History</router-link>
            </li>
          </template>
        </ul>

        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="userRole">
            <button class="btn btn-outline-light btn-sm mt-1" @click="handleLogout">Logout</button>
          </li>
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import authService from '../../services/auth';

export default {
  name: 'Navbar',
  data() {
    return {
      userRole: null
    };
  },
  created() {
    this.updateUserRole();
  },
  watch: {
    // Watch for route changes to update the navbar (e.g. after login/logout)
    $route() {
      this.updateUserRole();
    }
  },
  methods: {
    updateUserRole() {
      this.userRole = localStorage.getItem('user_role');
    },
    async handleLogout() {
      try {
        await authService.logout();
      } catch (err) {
        console.error("Logout error", err);
      } finally {
        // Clear local storage
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_id');
        localStorage.removeItem('profile_id');
        
        // Reset state
        this.userRole = null;
        
        // Redirect
        this.$router.push('/login');
      }
    }
  }
};
</script>