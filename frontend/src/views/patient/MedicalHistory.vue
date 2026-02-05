<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Medical History</h3>
      <button @click="triggerExport" class="btn btn-dark">Export to CSV</button>
    </div>

    <div v-if="history.length === 0" class="alert alert-secondary">No history found.</div>
    
    <div v-for="record in history" :key="record.id" class="card mb-3">
      <div class="card-header">
        {{ record.date }} - Dr. {{ record.doctor_name }}
      </div>
      <div class="card-body">
        <p><strong>Diagnosis:</strong> {{ record.diagnosis }}</p>
        <p><strong>Prescription:</strong> {{ record.prescription }}</p>
        <p class="text-muted"><small>{{ record.notes }}</small></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const history = ref([]);

onMounted(async () => {
  const res = await api.get('/patient/history');
  history.value = res.data;
});

const triggerExport = async () => {
  try {
    const res = await api.post('/patient/export');
    alert(res.data.message); // "Export job started..."
  } catch (err) {
    alert('Export failed');
  }
};
</script>