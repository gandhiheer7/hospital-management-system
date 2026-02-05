<template>
  <div>
    <h3>Manage Patients</h3>
    <table class="table table-hover mt-3">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Contact</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in patients" :key="p.id">
          <td>{{ p.name }}</td>
          <td>{{ p.email }}</td>
          <td>{{ p.contact_info }}</td>
          <td>
            <span class="badge" :class="p.is_blocked ? 'bg-danger' : 'bg-success'">
              {{ p.is_blocked ? 'Blocked' : 'Active' }}
            </span>
          </td>
          <td>
            <button v-if="!p.is_blocked" @click="toggleBlock(p.id, true)" class="btn btn-sm btn-danger">Block</button>
            <button v-else @click="toggleBlock(p.id, false)" class="btn btn-sm btn-secondary">Unblock</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const patients = ref([]);

const fetchPatients = async () => {
  const res = await api.get('/admin/patients');
  patients.value = res.data;
};

const toggleBlock = async (id, status) => {
  await api.put(`/admin/patients/${id}/block`, { is_blocked: status });
  fetchPatients();
};

onMounted(fetchPatients);
</script>