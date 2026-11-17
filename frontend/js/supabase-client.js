/**
 * AgriSense Supabase Client & API Service Module
 * Handles Authentication, Session Persistence, Storage, and Backend API Gateway
 */

// Supabase Configuration
const SUPABASE_CONFIG = {
  url: window.AGRISENSE_SUPABASE_URL || 'https://qxocrgejzvtgsdzjjewl.supabase.co',
  anonKey: window.AGRISENSE_SUPABASE_ANON_KEY || 'sb_publishable_wexU-OLQifldyWaWutyjCg_q38g-lv-'
};

// Backend API Base URL
const API_BASE = window.location.origin.includes('http') ? window.location.origin : 'http://localhost:5000';

class AgriSenseAuth {
  constructor() {
    this.client = null;
    this.session = null;
    this.user = null;
    this.initSupabase();
  }

  initSupabase() {
    if (window.supabase && typeof window.supabase.createClient === 'function') {
      try {
        if (!SUPABASE_CONFIG.url.includes('placeholder') && !SUPABASE_CONFIG.anonKey.includes('placeholder')) {
          this.client = window.supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);
        }
      } catch (err) {
        console.warn('[AgriSense] Supabase JS Client initialized in fallback/hybrid mode:', err);
      }
    }

    // Load cached session from localStorage
    const savedSession = localStorage.getItem('agrisense_session');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        this.session = parsed;
        this.user = parsed.user || parsed;
      } catch (e) {
        localStorage.removeItem('agrisense_session');
      }
    }
  }

  isConfigured() {
    return !!(this.client && !SUPABASE_CONFIG.url.includes('placeholder'));
  }

  async getSession() {
    if (this.isConfigured()) {
      try {
        const { data: { session }, error } = await this.client.auth.getSession();
        if (session && !error) {
          this.session = session;
          this.user = session.user;
          localStorage.setItem('agrisense_session', JSON.stringify(session));
          return session;
        }
      } catch (e) {
        console.warn('[AgriSense] Error retrieving Supabase session:', e);
      }
    }
    return this.session;
  }

  async getUser() {
    const session = await this.getSession();
    return session ? (session.user || session) : null;
  }

  getAccessToken() {
    if (this.session && this.session.access_token) {
      return this.session.access_token;
    }
    return localStorage.getItem('agrisense_token') || null;
  }

  async register({ email, password, firstName, lastName, phone }) {
    // 1. If Supabase Client is configured, register directly with Supabase
    if (this.isConfigured()) {
      try {
        const { data, error } = await this.client.auth.signUp({
          email,
          password,
          options: {
            data: {
              first_name: firstName,
              last_name: lastName || '',
              phone: phone || '',
              farmer_experience_level: 'Beginner',
              preferred_language: 'en'
            }
          }
        });
        if (error) throw error;
        if (data && data.session) {
          this.session = data.session;
          this.user = data.user;
          localStorage.setItem('agrisense_session', JSON.stringify(data.session));
          localStorage.setItem('agrisense_token', data.session.access_token);
        }
        return { success: true, data, message: 'Registration successful!' };
      } catch (err) {
        return { success: false, message: err.message || 'Supabase registration failed' };
      }
    }

    // 2. Fallback to Flask backend /api/auth/register
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName || '',
          phone: phone || ''
        })
      });
      const data = await res.json();
      if (data.success && data.user) {
        this.session = data.session || { user: data.user, access_token: data.token };
        this.user = data.user;
        localStorage.setItem('agrisense_session', JSON.stringify(this.session));
        if (data.token) localStorage.setItem('agrisense_token', data.token);
      }
      return data;
    } catch (err) {
      return { success: false, message: 'Could not connect to backend server. Make sure Flask is running.' };
    }
  }

  async login({ email, password, remember = false }) {
    // 1. If Supabase Client is configured
    if (this.isConfigured()) {
      try {
        const { data, error } = await this.client.auth.signInWithPassword({
          email,
          password
        });
        if (error) throw error;
        this.session = data.session;
        this.user = data.user;
        const storage = remember ? localStorage : sessionStorage;
        storage.setItem('agrisense_session', JSON.stringify(data.session));
        localStorage.setItem('agrisense_token', data.session.access_token);
        return { success: true, data, message: 'Signed in successfully!' };
      } catch (err) {
        return { success: false, message: err.message || 'Invalid credentials' };
      }
    }

    // 2. Fallback to Flask backend /api/auth/login
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, remember })
      });
      const data = await res.json();
      if (data.success && data.user) {
        this.session = data.session || { user: data.user, access_token: data.token };
        this.user = data.user;
        const storage = remember ? localStorage : sessionStorage;
        storage.setItem('agrisense_session', JSON.stringify(this.session));
        if (data.token) localStorage.setItem('agrisense_token', data.token);
      }
      return data;
    } catch (err) {
      return { success: false, message: 'Could not connect to backend server. Make sure Flask is running.' };
    }
  }

  async logout() {
    if (this.isConfigured()) {
      try {
        await this.client.auth.signOut();
      } catch (e) {
        console.warn('[AgriSense] SignOut error:', e);
      }
    }
    this.session = null;
    this.user = null;
    localStorage.removeItem('agrisense_session');
    localStorage.removeItem('agrisense_token');
    sessionStorage.removeItem('agrisense_session');
    return { success: true };
  }

  async forgotPassword(email) {
    if (this.isConfigured()) {
      try {
        const { data, error } = await this.client.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/login.html?type=recovery`
        });
        if (error) throw error;
        return { success: true, message: 'Password reset link sent to your email!' };
      } catch (err) {
        return { success: false, message: err.message };
      }
    }

    try {
      const res = await fetch(`${API_BASE}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      return await res.json();
    } catch (err) {
      return { success: false, message: 'Could not connect to server.' };
    }
  }

  async signInWithOAuth(provider) {
    if (this.isConfigured()) {
      try {
        const { data, error } = await this.client.auth.signInWithOAuth({
          provider,
          options: {
            redirectTo: `${window.location.origin}/index.html`
          }
        });
        if (error) throw error;
        return { success: true, data };
      } catch (err) {
        return { success: false, message: err.message };
      }
    }
    return { success: false, message: 'Supabase OAuth is not configured with client ID yet.' };
  }

  async sendPhoneOtp(phone) {
    if (this.isConfigured()) {
      try {
        const { data, error } = await this.client.auth.signInWithOtp({
          phone
        });
        if (error) throw error;
        return { success: true, message: 'OTP sent to ' + phone };
      } catch (err) {
        return { success: false, message: err.message };
      }
    }
    return { success: false, message: 'Supabase Phone/Twilio provider not configured yet.' };
  }

  async verifyPhoneOtp(phone, token) {
    if (this.isConfigured()) {
      try {
        const { data, error } = await this.client.auth.verifyOtp({
          phone,
          token,
          type: 'sms'
        });
        if (error) throw error;
        this.session = data.session;
        this.user = data.user;
        localStorage.setItem('agrisense_session', JSON.stringify(data.session));
        return { success: true, data };
      } catch (err) {
        return { success: false, message: err.message };
      }
    }
    return { success: false, message: 'OTP verification requires configured Supabase SMS provider.' };
  }
}

// Global Auth Instance
window.agriAuth = new AgriSenseAuth();

// Unified Secure API Client helper
window.agriApi = async function(path, method = 'GET', body = null) {
  const token = window.agriAuth ? window.agriAuth.getAccessToken() : null;
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const opts = { method, headers };
  if (body) {
    opts.body = typeof body === 'string' ? body : JSON.stringify(body);
  }

  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const res = await fetch(url, opts);
  if (!res.ok && res.status === 401) {
    console.warn('[AgriSense] Unauthorized request to', path);
  }
  return res.json();
};
