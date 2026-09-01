"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../../store/authStore";
import { authService } from "../../services/auth.service";
import { Shield, Lock, User, Key, KeyRound, AlertTriangle } from "lucide-react";

export default function LoginPage() {
  const [badge, setBadge] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [role, setRole] = useState("Investigating Officer");
  const [step, setStep] = useState(1); // 1: Credentials, 2: OTP
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);

  const roles = [
    "Investigating Officer",
    "Station Inspector",
    "District SP",
    "Intelligence Analyst",
    "System Administrator"
  ];

  const handleCredentialsSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!badge || !password) {
      setError("Badge number and security password are required.");
      return;
    }
    
    setIsLoading(true);
    // Simulate secure network handshaking
    setTimeout(() => {
      setIsLoading(false);
      setStep(2); // Proceed to OTP check
    }, 1200);
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    if (!otp) {
      setError("Secure token/OTP is required.");
      return;
    }

    if (otp !== "123456" && otp.length !== 6) {
      setError("Invalid security token. Please enter 6 digits (Try '123456' for simulation).");
      return;
    }

    setIsLoading(true);
    
    try {
      // Call backend API for real authentication
      const loginResponse = await authService.login(badge, password);
      
      setIsLoading(false);
      
      // We parse out minimal user details from the badge/role. 
      // In a real app, the backend might return user details with the token,
      // or we'd make a /users/me call. For now, we store what we know.
      const user = {
        id: "USR-" + badge,
        badge_number: badge,
        role: role,
        first_name: badge.startsWith("SP") ? "SP Kumar" : "Officer",
        last_name: "K."
      };
      
      setAuth(user, loginResponse.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setIsLoading(false);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(`Secure link failed: ${err.response.data.detail}`);
      } else {
        setError("Secure link failed. Please check your credentials and retry.");
      }
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-[#030914] px-4 py-12 overflow-hidden">
      
      {/* Visual background grids and nodes */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#081730_1px,transparent_1px),linear-gradient(to_bottom,#081730_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-35" />
      <div className="absolute top-1/4 left-1/4 h-[400px] w-[400px] rounded-full bg-blue-700/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 h-[400px] w-[400px] rounded-full bg-indigo-700/10 blur-[120px] pointer-events-none" />

      {/* Main Container */}
      <div className="relative w-full max-w-xl z-10">
        
        {/* Crest & Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-500 to-amber-300 p-0.5 shadow-2xl shadow-amber-500/20 mb-4 animate-pulse duration-3000">
            <div className="flex h-full w-full items-center justify-center bg-[#030914] rounded-[14px]">
              <Shield className="h-10 w-10 text-amber-400" />
            </div>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl bg-clip-text bg-gradient-to-r from-slate-100 via-slate-200 to-slate-400">
            LINKRA
          </h1>
          <p className="text-sm font-semibold tracking-widest text-blue-400 uppercase mt-1">
            AI-Powered Criminal Intelligence Network
          </p>
          <p className="text-xs text-slate-500 mt-2 max-w-sm">
            National Criminal Intelligence Network • Law Enforcement Only
          </p>
        </div>

        {/* Form Console Container */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-8 shadow-2xl shadow-slate-950/50">
          
          {/* Classification Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
            <span className="text-[10px] font-bold text-red-500 bg-red-500/15 border border-red-500/30 px-2.5 py-0.5 rounded tracking-wider uppercase">
              CONFIDENTIAL // NO-FORN
            </span>
            <span className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping" />
              PORT SECURE
            </span>
          </div>

          {error && (
            <div className="flex items-start gap-2.5 p-3.5 mb-6 text-sm text-red-400 bg-red-500/10 rounded-xl border border-red-500/25">
              <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Security Alert:</span> {error}
              </div>
            </div>
          )}

          {step === 1 ? (
            /* STEP 1: CREDENTIALS */
            <form onSubmit={handleCredentialsSubmit} className="space-y-5">
              
              {/* Role Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Access Clearance Level</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {roles?.map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRole(r)}
                      className={`px-3 py-2 text-left rounded-xl border text-[11px] font-medium transition-all ${
                        role === r 
                          ? "bg-blue-600/15 border-blue-500/80 text-blue-400 font-semibold" 
                          : "bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              {/* Badge Number */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Officer Badge Number</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-500">
                    <User className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    required
                    placeholder="e.g. LEO-4892-IND"
                    className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all font-mono"
                    value={badge}
                    onChange={(e) => setBadge(e.target.value)}
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">Agency Security Key</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-500">
                    <Key className="h-4 w-4" />
                  </div>
                  <input
                    type="password"
                    required
                    placeholder="••••••••••••••"
                    className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all font-mono"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="relative w-full py-3 px-4 mt-2 overflow-hidden bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-blue-500/15 active:translate-y-px disabled:opacity-50"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    <span>Cryptographic Handshake...</span>
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <KeyRound className="h-4 w-4" />
                    <span>Initiate Secure Authentication</span>
                  </span>
                )}
              </button>

            </form>
          ) : (
            /* STEP 2: OTP */
            <form onSubmit={handleOtpSubmit} className="space-y-6">
              
              <div className="text-center bg-slate-950/40 border border-slate-800/60 rounded-xl p-4 mb-4">
                <p className="text-xs text-slate-300 font-medium">
                  CLEARANCE ROLE: <span className="text-blue-400 font-semibold">{role}</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Secure access token sent to registered device linked to <span className="font-mono text-slate-300">{badge}</span>
                </p>
              </div>

              {/* OTP Code */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">6-Digit Access Token (OTP)</label>
                  <span className="text-[10px] text-slate-500 font-mono">Use "123456" for demo</span>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-500">
                    <Lock className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    maxLength={6}
                    required
                    placeholder="Enter 6-digit verification code"
                    className="w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-center text-lg font-bold tracking-widest text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all font-mono"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  />
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 mt-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="w-1/3 py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold rounded-xl border border-slate-700 transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-blue-500/15 active:translate-y-px disabled:opacity-50"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      <span>Verifying Token...</span>
                    </span>
                  ) : (
                    <span>Access Command Console</span>
                  )}
                </button>
              </div>

            </form>
          )}

        </div>

        {/* Footer Notes */}
        <div className="text-center mt-6">
          <p className="text-[10px] text-slate-600">
            WARNING: Unauthorized access to this platform constitutes a federal offence in violation of the Information Technology Act. All access sessions, IPs, and actions are logged and subject to audit by the Cyber Crime Division.
          </p>
        </div>

      </div>
    </div>
  );
}
