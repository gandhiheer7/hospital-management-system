<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">Patient Registration</div>
          <div class="card-body">

            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>

            <form v-if="!success" @submit.prevent="handleRegister">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="form.name" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Email Address</label>
                <input type="email" class="form-control" v-model="form.email" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="form.password" required>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Date of Birth</label>
                  <input type="date" class="form-control" v-model="form.dob">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Contact Number</label>
                  <input type="text" class="form-control" v-model="form.contact_info">
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" v-model="form.address" rows="2"></textarea>
              </div>

              <button type="submit" class="btn btn-primary w-100">Register</button>
            </form>

            <div class="mt-3 text-center">
              <p>Already have an account? <router-link to="/login">Login here</router-link></p>
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
  name: 'Register',
  data() {
    return {
      form: {
        name: '',
        email: '',
        password: '',
        dob: '',
        contact_info: '',
        address: ''
      },
      error: '',
      success: ''
    };
  },
  methods: {
    async handleRegister() {
      this.error = '';
      this.success = '';
      
      try {
        await authService.register(this.form);
        this.success = 'Registration successful! You can now log in.';
        this.form = {}; // Clear form
      } catch (err) {
        if (err.response && err.response.data && err.response.data.message) {
          this.error = err.response.data.message;
        } else {
          this.error = 'Registration failed. Please try again.';
        }
      }
    }
  }
};
</script>