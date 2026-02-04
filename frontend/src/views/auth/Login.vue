<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-header">Login</div>
          <div class="card-body">
            
            <div v-if="error" class="alert alert-danger">
              {{ error }}
            </div>

            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="email" class="form-label">Email address</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email" 
                  v-model="email" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="password" 
                  required
                >
              </div>

              <button 
                type="submit" 
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </form>

            <div class="mt-3 text-center">
              <p>
                Don't have an account?
                <router-link to="/register">Register as a Patient</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '../../services/auth';

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      error: '',
      loading: false
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      this.loading = true;

      // Clear any stale auth data
      localStorage.removeItem('user_role');
      localStorage.removeItem('user_id');
      localStorage.removeItem('profile_id');

      try {
        const response = await authService.login({
          email: this.email,
          password: this.password
        });

        const { role, user_id, profile_id } = response.data;
        const allowedRoles = ['admin', 'doctor', 'patient'];

        if (!allowedRoles.includes(role)) {
          throw new Error('Invalid user role received from server');
        }

        // Save session details for routing logic
        localStorage.setItem('user_role', role);
        localStorage.setItem('user_id', user_id);

        if (profile_id) {
          localStorage.setItem('profile_id', profile_id);
        }

        // Redirect based on role
        this.$router.push(`/${role}/dashboard`);

      } catch (err) {
        if (err.response?.data?.message) {
          this.error = err.response.data.message;
        } else {
          this.error = 'Login failed. Please check your credentials.';
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>