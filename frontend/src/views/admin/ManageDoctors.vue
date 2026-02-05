<template>
  <div>
    <h3>Manage Doctors</h3>
    
    <div class="card mb-4 p-3 bg-light">
      <h5>Add New Doctor</h5>
      <form @submit.prevent="addDoctor">
        <div class="row">
          <div class="col-md-3 mb-2"><input v-model="form.name" placeholder="Name" class="form-control" required /></div>
          <div class="col-md-3 mb-2"><input v-model="form.email" type="email" placeholder="Email" class="form-control" required /></div>
          <div class="col-md-3 mb-2"><input v-model="form.password" type="password" placeholder="Password" class="form-control" required /></div>
          <div class="col-md-3 mb-2">
            <select v-model="form.specialization_id" class="form-select" required>
              <option disabled value="">Specialization</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
            </select>
          </div>
          <div class="col-md-12 text-end">
            <button class="btn btn-primary">Add Doctor</button>
          </div>
        </div>
      </form>
    </div>

    <div class="mb-3">
      <input v-model="searchQuery" class="form-control" placeholder="Search by name or specialization..." />
    </div>

    <div class="table-responsive">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>Name</th>
            <th>Specialization</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in filteredDoctors" :key="doc.id">
            <td>{{ doc.name }}</td>
            <td>{{ doc.specialization }}</td>
            <td>
              <span class="badge" :class="doc.is_approved ? 'bg-success' : 'bg-secondary'">
                {{ doc.is_approved ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <button @click="openEdit(doc)" class="btn btn-sm btn-info me-1">Edit</button>
              <button v-if="doc.is_approved" @click="toggleStatus(doc.id, false)" class="btn btn-sm btn-warning me-1">Revoke</button>
              <button v-else @click="toggleStatus(doc.id, true)" class="btn btn-sm btn-success me-1">Approve</button>
              <button @click="deleteDoctor(doc.id)" class="btn btn-sm btn-danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="editingDoc" class="modal d-block" style="background: rgba(0,0,0,0.5)">
       <div class="modal-dialog">
         <div class="modal-content">
           <div class="modal-header"><h5>Edit Doctor</h5></div>
           <div class="modal-body">
             <label>Name</label>
             <input v-model="editingDoc.name" class="form-control mb-2">
             <label>Specialization</label>
             <select v-model="editingDoc.specialization_id" class="form-select">
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
             </select>
           </div>
           <div class="modal-footer">
             <button @click="editingDoc=null" class="btn btn-secondary">Cancel</button>
             <button @click="saveEdit" class="btn btn-primary">Save Changes</button>
           </div>
         </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../../services/api';

const doctors = ref([]);
const departments = ref([]);
const searchQuery = ref('');
const form = reactive({ name: '', email: '', password: '', specialization_id: '' });
const editingDoc = ref(null);

const fetchData = async () => {
  const [docRes, deptRes] = await Promise.all([
    api.get('/admin/doctors'),
    api.get('/admin/departments')
  ]);
  doctors.value = docRes.data;
  departments.value = deptRes.data;
};

// Client-side Search Logic
const filteredDoctors = computed(() => {
  const q = searchQuery.value.toLowerCase();
  return doctors.value.filter(d => 
    d.name.toLowerCase().includes(q) || d.specialization.toLowerCase().includes(q)
  );
});

const addDoctor = async () => {
  try {
    await api.post('/admin/doctors', form);
    alert('Doctor added');
    fetchData();
    form.name = ''; form.email = ''; form.password = '';
  } catch (err) { alert(err.response?.data?.message || 'Error'); }
};

const toggleStatus = async (id, status) => {
  await api.put(`/admin/doctors/${id}/status`, { is_approved: status });
  fetchData();
};

const deleteDoctor = async (id) => {
  if(!confirm('Are you sure? This will remove the doctor and their account.')) return;
  try {
    await api.delete(`/admin/doctors/${id}`);
    fetchData();
  } catch (err) { alert('Failed to delete'); }
};

const openEdit = (doc) => {
  editingDoc.value = { ...doc }; // Clone object
};

const saveEdit = async () => {
  try {
    await api.put(`/admin/doctors/${editingDoc.value.id}`, {
      name: editingDoc.value.name,
      specialization_id: editingDoc.value.specialization_id
    });
    editingDoc.value = null;
    fetchData();
  } catch (err) { alert('Update failed'); }
};

onMounted(fetchData);
</script>