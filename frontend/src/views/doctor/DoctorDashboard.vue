<template>
  <div>
    <h3>Doctor Dashboard</h3>
    
    <div class="card mb-4 shadow-sm">
      <div class="card-body">
         <h5>Update Availability</h5>
         <p class="small text-muted">Format: JSON {"Monday": ["09:00", "10:00"]}</p>
         <textarea v-model="scheduleJson" class="form-control" rows="3"></textarea>
         <button @click="updateSchedule" class="btn btn-secondary mt-2">Update Schedule</button>
      </div>
    </div>

    <h4 class="text-primary">1. Upcoming Appointments</h4>
    <div v-if="upcomingAppointments.length === 0" class="alert alert-light mb-4">No upcoming appointments.</div>
    
    <div v-for="apt in upcomingAppointments" :key="apt.id" class="card mb-3 border-primary shadow-sm">
      <div class="card-body d-flex justify-content-between align-items-center">
        <div>
          <h5>{{ apt.patient_name }}</h5>
          <p class="mb-1">{{ apt.date }} at {{ apt.time_slot }}</p>
          <span class="badge bg-info">{{ apt.status }}</span>
        </div>
        <div>
          <button @click="openCompleteModal(apt)" class="btn btn-success">Complete Visit</button>
        </div>
      </div>
    </div>

    <hr class="my-5">

    <h4 class="text-success">2. Assigned Patients (Treated)</h4>
    <div v-if="assignedPatients.length === 0" class="alert alert-light">No patients treated yet.</div>
    
    <div class="table-responsive" v-else>
        <table class="table table-bordered table-hover">
            <thead class="table-light">
                <tr>
                    <th>Patient Name</th>
                    <th>Contact</th>
                    <th>Last Visit</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="p in assignedPatients" :key="p.patient_id">
                    <td>{{ p.patient_name }}</td>
                    <td>{{ p.contact }}</td>
                    <td>{{ p.last_visit }}</td>
                    <td>
                        <button @click="viewHistory(p.patient_id, p.patient_name)" class="btn btn-sm btn-outline-dark">
                            View Full History
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div v-if="selectedApt" class="modal d-block" style="background: rgba(0,0,0,0.5)">
       <div class="modal-dialog">
         <div class="modal-content">
           <div class="modal-header"><h5>Complete Appointment</h5></div>
           <div class="modal-body">
             <input v-model="treatment.diagnosis" placeholder="Diagnosis" class="form-control mb-2">
             <input v-model="treatment.prescription" placeholder="Prescription" class="form-control mb-2">
             <textarea v-model="treatment.notes" placeholder="Notes" class="form-control mb-2"></textarea>
           </div>
           <div class="modal-footer">
             <button @click="selectedApt=null" class="btn btn-secondary">Close</button>
             <button @click="submitTreatment" class="btn btn-primary">Save</button>
           </div>
         </div>
       </div>
    </div>

    <div v-if="selectedPatientHistory" class="modal d-block" style="background: rgba(0,0,0,0.5)">
       <div class="modal-dialog modal-lg">
         <div class="modal-content">
           <div class="modal-header">
               <h5>Medical History: {{ selectedPatientName }}</h5>
               <button @click="selectedPatientHistory=null" class="btn-close"></button>
           </div>
           <div class="modal-body">
             <div v-if="selectedPatientHistory.length === 0">No past records found.</div>
             <ul class="list-group">
                 <li v-for="(rec, idx) in selectedPatientHistory" :key="idx" class="list-group-item">
                     <strong>Date:</strong> {{ rec.date }} <br>
                     <strong>Doctor:</strong> {{ rec.doctor_name }} <br>
                     <strong>Diagnosis:</strong> {{ rec.diagnosis }} <br>
                     <strong>Prescription:</strong> {{ rec.prescription }}
                 </li>
             </ul>
           </div>
           <div class="modal-footer">
             <button @click="selectedPatientHistory=null" class="btn btn-secondary">Close</button>
           </div>
         </div>
       </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../services/api';

const upcomingAppointments = ref([]);
const assignedPatients = ref([]);
const scheduleJson = ref('{}');
const selectedApt = ref(null);
const treatment = reactive({ diagnosis: '', prescription: '', notes: '' });

// History State
const selectedPatientHistory = ref(null);
const selectedPatientName = ref('');

const fetchDashboard = async () => {
  const res = await api.get('/doctor/dashboard');
  upcomingAppointments.value = res.data.upcoming_appointments;
  assignedPatients.value = res.data.assigned_patients; // New Data
};

const updateSchedule = async () => {
  try {
    const json = JSON.parse(scheduleJson.value);
    await api.put('/doctor/availability', { schedule: json });
    alert('Availability updated');
  } catch (e) {
    alert('Invalid JSON format');
  }
};

const openCompleteModal = (apt) => {
  selectedApt.value = apt;
};

// View History for Assigned Patient
const viewHistory = async (patientId, name) => {
    try {
        const res = await api.get(`/doctor/patient/${patientId}/history`);
        selectedPatientHistory.value = res.data.history;
        selectedPatientName.value = name;
    } catch (e) {
        alert('Could not load history');
    }
};

const submitTreatment = async () => {
  try {
    await api.post(`/doctor/appointment/${selectedApt.value.id}/complete`, treatment);
    alert('Visit Completed');
    selectedApt.value = null;
    fetchDashboard();
  } catch (e) {
    alert('Error');
  }
};

onMounted(fetchDashboard);
</script>