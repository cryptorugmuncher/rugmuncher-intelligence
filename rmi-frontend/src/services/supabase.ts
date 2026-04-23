/**
 * Supabase Client
 * ===============
 * Connects to Supabase for auth and persistent data
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://ufblzfxqwgaekrewncbi.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || 'YOUR_SUPABASE_KEY_HERE';

export const supabase = createClient(supabaseUrl, supabaseKey);

// Auth helpers
export const auth = {
  signUp: (email: string, password: string) =>
    supabase.auth.signUp({ email, password }),

  signIn: (email: string, password: string) =>
    supabase.auth.signInWithPassword({ email, password }),

  signOut: () => supabase.auth.signOut(),

  getUser: () => supabase.auth.getUser(),

  onAuthChange: (callback: (event: string, session: any) => void) =>
    supabase.auth.onAuthStateChange(callback),
};

// Database helpers
export const db = {
  // Health check
  health: async () => {
    const { data, error } = await supabase
      .from('system_health_log')
      .select('*')
      .limit(1);
    return { data, error, connected: !error };
  },

  // Wallets
  wallets: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('wallets')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    getByAddress: async (address: string) => {
      const { data, error } = await supabase
        .from('wallets')
        .select('*')
        .eq('address', address)
        .single();
      return { data, error };
    },

    create: async (wallet: { address: string; chain?: string; tags?: string[] }) => {
      const { data, error } = await supabase
        .from('wallets')
        .insert([{ ...wallet, scanned_at: new Date().toISOString() }])
        .select();
      return { data, error };
    },
  },

  // Investigations
  investigations: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('investigations')
        .select('*')
        .order('updated_at', { ascending: false });
      return { data, error };
    },

    getById: async (id: string) => {
      const { data, error } = await supabase
        .from('investigations')
        .select('*')
        .eq('id', id)
        .single();
      return { data, error };
    },

    create: async (investigation: {
      title: string;
      description?: string;
      wallet_addresses?: string[];
      status?: string;
    }) => {
      const { data, error } = await supabase
        .from('investigations')
        .insert([{ ...investigation, created_at: new Date().toISOString() }])
        .select();
      return { data, error };
    },
  },

  // Evidence
  evidence: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('evidence')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    getByInvestigation: async (investigationId: string) => {
      const { data, error } = await supabase
        .from('evidence')
        .select('*')
        .eq('investigation_id', investigationId)
        .order('collected_at', { ascending: false });
      return { data, error };
    },

    create: async (evidence: {
      investigation_id?: string;
      evidence_type: string;
      source?: string;
      content?: any;
      title?: string;
      description?: string;
      storage_path?: string;
      source_url?: string;
      confidence?: number;
    }) => {
      const { data, error } = await supabase
        .from('evidence')
        .insert([{ ...evidence, collected_at: new Date().toISOString() }])
        .select();
      return { data, error };
    },

    update: async (id: string, updates: any) => {
      const { data, error } = await supabase
        .from('evidence')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select();
      return { data, error };
    },
  },

  // Users (for admin user management)
  users: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    getById: async (id: string) => {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', id)
        .single();
      return { data, error };
    },

    update: async (id: string, updates: any) => {
      const { data, error } = await supabase
        .from('users')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select();
      return { data, error };
    },

    ban: async (id: string, reason: string, duration?: number) => {
      const { data, error } = await supabase
        .from('users')
        .update({
          banned: true,
          ban_reason: reason,
          ban_expires_at: duration ? new Date(Date.now() + duration * 86400000).toISOString() : null,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select();
      return { data, error };
    },

    unban: async (id: string) => {
      const { data, error } = await supabase
        .from('users')
        .update({
          banned: false,
          ban_reason: null,
          ban_expires_at: null,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
        .select();
      return { data, error };
    },
  },

  // Feature Flags
  features: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('feature_flags')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    create: async (feature: any) => {
      const { data, error } = await supabase
        .from('feature_flags')
        .insert([{ ...feature, created_at: new Date().toISOString() }])
        .select();
      return { data, error };
    },

    update: async (id: string, updates: any) => {
      const { data, error } = await supabase
        .from('feature_flags')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select();
      return { data, error };
    },

    delete: async (id: string) => {
      const { data, error } = await supabase
        .from('feature_flags')
        .delete()
        .eq('id', id)
        .select();
      return { data, error };
    },
  },

  // API Keys
  apiKeys: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('api_keys')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    create: async (key: any) => {
      const { data, error } = await supabase
        .from('api_keys')
        .insert([{ ...key, created_at: new Date().toISOString() }])
        .select();
      return { data, error };
    },

    revoke: async (id: string) => {
      const { data, error } = await supabase
        .from('api_keys')
        .update({ status: 'revoked', updated_at: new Date().toISOString() })
        .eq('id', id)
        .select();
      return { data, error };
    },

    delete: async (id: string) => {
      const { data, error } = await supabase
        .from('api_keys')
        .delete()
        .eq('id', id)
        .select();
      return { data, error };
    },
  },

  // Trenches Community
  trenches: {
    getAllPosts: async () => {
      const { data, error } = await supabase
        .from('trenches_posts')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    updatePost: async (id: string, updates: any) => {
      const { data, error } = await supabase
        .from('trenches_posts')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select();
      return { data, error };
    },

    deletePost: async (id: string) => {
      const { data, error } = await supabase
        .from('trenches_posts')
        .delete()
        .eq('id', id)
        .select();
      return { data, error };
    },
  },

  // Rug Pull Rehab Bookings
  rehab: {
    getAllBookings: async () => {
      const { data, error } = await supabase
        .from('rehab_bookings')
        .select('*')
        .order('date', { ascending: true });
      return { data, error };
    },

    updateBooking: async (id: string, updates: any) => {
      const { data, error } = await supabase
        .from('rehab_bookings')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select();
      return { data, error };
    },

    createBooking: async (booking: any) => {
      const { data, error } = await supabase
        .from('rehab_bookings')
        .insert([{ ...booking, created_at: new Date().toISOString() }])
        .select();
      return { data, error };
    },
  },

  // Payments & Revenue
  payments: {
    getAll: async () => {
      const { data, error } = await supabase
        .from('payments')
        .select('*')
        .order('created_at', { ascending: false });
      return { data, error };
    },

    getStats: async () => {
      const { data, error } = await supabase
        .from('payment_stats')
        .select('*')
        .single();
      return { data, error };
    },
  },
};

export default supabase;
