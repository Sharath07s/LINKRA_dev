"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../store/authStore";
import { Shield } from "lucide-react";

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Immediate redirect based on security status
    if (isAuthenticated) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex h-screen w-screen items-center justify-center bg-[#030914] text-white">
      <div className="flex flex-col items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-amber-300 p-0.5 shadow-2xl shadow-amber-500/20 animate-pulse">
          <div className="flex h-full w-full items-center justify-center bg-[#030914] rounded-[10px]">
            <Shield className="h-8 w-8 text-amber-400" />
          </div>
        </div>
        <div className="flex flex-col items-center gap-1.5">
          <h2 className="text-sm font-bold tracking-wider text-slate-250 uppercase">LINKRA Secure Gateway [TEST]</h2>
          <p className="text-xs text-[#666666]">Initiating cryptographically secure network handshake...</p>
        </div>
        <div className="h-1.5 w-48 bg-[#080808] rounded-full overflow-hidden border border-[#222222]">
          <div className="h-full bg-gradient-to-r from-blue-600 to-indigo-500 rounded-full w-2/3 animate-pulse" />
        </div>
      </div>
    </div>
  );
}
