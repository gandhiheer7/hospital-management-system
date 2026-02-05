<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">Edit Profile</div>
        <div class="card-body">
          <form @submit.prevent="updateProfile">
            <div class="mb-3">
              <label>Name</label>
              <input v-model="form.name" class="form-control" />
            </div>
            <div class="mb-3">
              <label>Contact Info</label>
              <input v-model="form.contact_info" class="form-control" />
            </div>
            <div class="mb-3">
              <label>Address</label>
              <textarea v-model="form.address" class="form-control"></textarea>
            </div>
            <button class="btn btn-primary w-100">Save Changes</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import api from '../../services/api';

const form = reactive({ name: '', contact_info: '', address: '' });

// Note: Backend 'get profile' was not in requirements, so form starts empty.
// User can overwrite data.

const updateProfile = async () => {
  try {
    await api.put('/patient/profile', form);
    alert('Profile Updated');
  } catch (err) {
    alert('Failed to update');
  }
};
</script>