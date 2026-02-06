<template>
  <div>
    <h3>Manage Patients</h3>
    
    <div class="mb-3">
        <input v-model="searchQuery" class="form-control" placeholder="Search patients by Name or Contact..." />
    </div>

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
        <tr v-for="p in filteredPatients" :key="p.id">
          <td>{{ p.name }}</td>
          <td>{{ p.email }}</td>
          <td>{{ p.contact_info }}</td>
          <td>
            <span class="badge" :class="p.is_blocked ? 'bg-danger' : 'bg-success'">
              {{ p.is_blocked ? 'Blocked' : 'Active' }}
            </span>
          </td>
          <td>
            <button @click="openEdit(p)" class="btn btn-sm btn-info me-1">Edit</button>
            
            <button v-if="!p.is_blocked" @click="toggleBlock(p.id, true)" class="btn btn-sm btn-danger">Block</button>
            <button v-else @click="toggleBlock(p.id, false)" class="btn btn-sm btn-secondary">Unblock</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editingPatient" class="modal d-block" style="background: rgba(0,0,0,0.5)">
       <div class="modal-dialog">
         <div class="modal-content">
           <div class="modal-header"><h5>Edit Patient</h5></div>
           <div class="modal-body">
             <label>Name</label>
             <input v-model="editingPatient.name" class="form-control mb-2">
             <label>Contact Info</label>
             <input v-model="editingPatient.contact_info" class="form-control mb-2">
           </div>
           <div class="modal-footer">
             <button @click="editingPatient=null" class="btn btn-secondary">Cancel</button>
             <button @click="saveEdit" class="btn btn-primary">Save Changes</button>
           </div>
         </div>
       </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../services/api';

const patients = ref([]);
const searchQuery = ref('');
const editingPatient = ref(null);

const fetchPatients = async () => {
  const res = await api.get('/admin/patients');
  patients.value = res.data;
};

// NEW: Search Logic
const filteredPatients = computed(() => {
    if (!searchQuery.value) return patients.value;
    const q = searchQuery.value.toLowerCase();
    return patients.value.filter(p => 
        p.name.toLowerCase().includes(q) || 
        (p.contact_info && p.contact_info.toLowerCase().includes(q))
    );
});

const openEdit = (p) => {
    editingPatient.value = { ...p };
};

const saveEdit = async () => {
    try {
        await api.put(`/admin/patients/${editingPatient.value.id}`, {
            name: editingPatient.value.name,
            contact_info: editingPatient.value.contact_info
        });
        editingPatient.value = null;
        fetchPatients();
    } catch (err) {
        alert('Update failed');
    }
};

const toggleBlock = async (id, status) => {
  await api.put(`/admin/patients/${id}/block`, { is_blocked: status });
  fetchPatients();
};

onMounted(fetchPatients);
</script>