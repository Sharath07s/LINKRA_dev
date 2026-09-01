import os
from pathlib import Path

SRC_DIR = Path("/Users/sharathhn/SIH_26189/ICA_ai/frontend/src")

ROUTES = [
    "ingestion",
    "entities",
    "resolution",
    "anomalies",
    "network-analysis"
]

ROUTE_TITLES = {
    "ingestion": "Data Ingestion",
    "entities": "Entity Management",
    "resolution": "Entity Resolution",
    "anomalies": "Anomaly Detection",
    "network-analysis": "Network Analysis"
}

def create_frontend_boundaries():
    # 1. Create Route Placeholders
    app_dir = SRC_DIR / "app"
    for route in ROUTES:
        route_dir = app_dir / route
        route_dir.mkdir(parents=True, exist_ok=True)
        page_path = route_dir / "page.tsx"
        title = ROUTE_TITLES[route]
        with open(page_path, "w") as f:
            f.write(f'''import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';

export default function {route.replace("-", "").capitalize()}Page() {{
  return (
    <DashboardLayout>
      <div className="flex flex-col items-center justify-center h-full min-h-[500px]">
        <h1 className="text-2xl font-bold mb-4">{title}</h1>
        <p className="text-gray-500">
          This feature is part of the SIH26189 architecture but is <strong>NOT YET IMPLEMENTED</strong>.
        </p>
      </div>
    </DashboardLayout>
  );
}}
''')
        print(f"Created route placeholder: /app/{route}")

    # 2. Create API Client
    lib_dir = SRC_DIR / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)
    api_client_path = lib_dir / "api-client.ts"
    with open(api_client_path, "w") as f:
        f.write('''/**
 * Centralized API Client (Phase 1 Target)
 * STATUS: NOT_IMPLEMENTED (Used as placeholder for future refactor)
 */
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
''')
    print("Created centralized API client: src/lib/api-client.ts")

if __name__ == "__main__":
    create_frontend_boundaries()
