import apiClient from './api';

export default {
  /**
   * Logs the user in.
   * Payload: { email, password }
   * Backend returns: { message, role, user_id, profile_id? } + Session Cookie
   */
  login(credentials) {
    return apiClient.post('/login', credentials);
  },

  /**
   * Registers a new patient.
   * Payload: { email, password, name, dob, contact_info, address }
   */
  register(data) {
    return apiClient.post('/register', data);
  },

  /**
   * Logs the user out.
   * Backend clears the session cookie.
   */
  logout() {
    return apiClient.post('/logout');
  }
};