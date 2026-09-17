import { create } from "zustand";

export interface UserState {
  userId: string | null;
  email: string | null;
  role: string | null;
  isPro: boolean;
  token: string | null;
  setAuth: (token: string, userId: string, email: string, role: string, isPro: boolean) => void;
  logout: () => void;
}

export interface DocumentItem {
  id: string;
  original_filename: string;
  sha256_hash: string;
  file_size: number;
  mime_type: string;
  page_count: number;
  is_sanitized: boolean;
  created_at: string;
}

export interface AppStore extends UserState {
  theme: "dark" | "light";
  toggleTheme: () => void;
  setTheme: (theme: "dark" | "light") => void;

  currentDocument: DocumentItem | null;
  documents: DocumentItem[];
  setCurrentDocument: (doc: DocumentItem | null) => void;
  setDocuments: (docs: DocumentItem[]) => void;
  addDocument: (doc: DocumentItem) => void;
}

export const useAppStore = create<AppStore>((set) => ({
  // Theme State
  theme: (typeof window !== "undefined" && (localStorage.getItem("spdf_theme") as "dark" | "light")) || "light",

  toggleTheme: () => {
    set((state) => {
      const nextTheme = state.theme === "dark" ? "light" : "dark";
      if (typeof window !== "undefined") {
        localStorage.setItem("spdf_theme", nextTheme);
        if (nextTheme === "dark") {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      }
      return { theme: nextTheme };
    });
  },

  setTheme: (theme) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("spdf_theme", theme);
      if (theme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
    set({ theme });
  },

  userId: typeof window !== "undefined" ? localStorage.getItem("spdf_user_id") : null,
  email: typeof window !== "undefined" ? localStorage.getItem("spdf_user_email") : null,
  role: typeof window !== "undefined" ? localStorage.getItem("spdf_user_role") : null,
  isPro: typeof window !== "undefined" ? localStorage.getItem("spdf_is_pro") === "true" : false,
  token: typeof window !== "undefined" ? localStorage.getItem("spdf_access_token") : null,

  currentDocument: null,
  documents: [],

  setAuth: (token, userId, email, role, isPro) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("spdf_access_token", token);
      localStorage.setItem("spdf_user_id", userId);
      localStorage.setItem("spdf_user_email", email);
      localStorage.setItem("spdf_user_role", role);
      localStorage.setItem("spdf_is_pro", String(isPro));
    }
    set({ token, userId, email, role, isPro });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("spdf_access_token");
      localStorage.removeItem("spdf_user_id");
      localStorage.removeItem("spdf_user_email");
      localStorage.removeItem("spdf_user_role");
      localStorage.removeItem("spdf_is_pro");
    }
    set({ token: null, userId: null, email: null, role: null, isPro: false, currentDocument: null, documents: [] });
  },

  setCurrentDocument: (doc) => set({ currentDocument: doc }),
  setDocuments: (docs) => set({ documents: docs }),
  addDocument: (doc) => set((state) => ({ documents: [doc, ...state.documents], currentDocument: doc })),
}));
