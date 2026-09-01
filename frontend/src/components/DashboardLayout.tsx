"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "../store/authStore";
import Link from "next/link";
import { 
  LayoutDashboard, 
  Map, 
  Network, 
  FolderOpen, 
  MessageSquare,
  FileText,
  Menu,
  Bell,
  Search,
  LogOut,
  ShieldCheck,
  X,
  User,
  Globe,
  Lock,
  ShieldAlert,
  Home, 
  Users, 
  Settings, 
  FileSearch, 
  HelpCircle, 
  Shield,
  Monitor,
  Activity,
  Radar,
  AlertTriangle,
  Database,
  Bot
} from "lucide-react";
import GlobalSearchBar from "./GlobalSearchBar";
import IntelligenceFeedTicker from "./IntelligenceFeedTicker";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, isAuthenticated, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [notificationsCount, setNotificationsCount] = useState(3);
  const [language, setLanguage] = useState<"EN" | "KA">("EN");

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background text-foreground">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-sm font-medium text-muted-foreground">Verifying security credentials...</p>
        </div>
      </div>
    );
  }

  const role = user?.role || "OFFICER";

  const navGroups = [
    {
      group: "OPERATIONS",
      items: [
        { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        { name: "Investigations", href: "/investigations", icon: FileSearch },
      ]
    },
    {
      group: "INTELLIGENCE",
      items: [
        { name: "Entities", href: "/entities", icon: Users },
        { name: "Knowledge Graph", href: "/knowledge-graph", icon: Network },
        { name: "Intelligence", href: "/intelligence", icon: Radar },
        { name: "Intelligence Map", href: "/map", icon: Map },
        { name: "Timeline", href: "/timeline", icon: Activity },
      ]
    },
    {
      group: "EVIDENCE",
      items: [
        { name: "Data Sources", href: "/data-sources", icon: Database },
        { name: "Evidence", href: "/evidence", icon: FolderOpen },
        { name: "Reports", href: "/reports", icon: FileText },
      ]
    },
    {
      group: "ASSISTANCE",
      items: [
        { name: "AI Copilot", href: "/copilot", icon: Bot },
      ]
    },
    ...(role === "ADMIN" ? [{
      group: "SYSTEM",
      items: [
        { name: "Administration", href: "/admin", icon: Settings },
      ]
    }] : [])
  ];

  return (
    <div className="flex min-h-screen bg-background text-foreground font-sans antialiased selection:bg-primary/30 selection:text-primary-foreground">
      
      {/* Sidebar - Desktop */}
      <aside 
        className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col border-r border-border bg-sidebar transition-all duration-300 ${
          isSidebarOpen ? "w-64" : "w-20"
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          <div className="flex items-center gap-3 overflow-hidden">
            {/* Crest SVG */}
            <div className="flex-shrink-0 bg-gradient-to-tr from-amber-500 to-yellow-300 p-1.5 rounded-lg shadow-lg shadow-amber-500/20">
              <svg className="h-5 w-5 text-slate-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col">
                <span className="text-sm font-bold tracking-wider text-foreground uppercase">LINKRA</span>
                <span className="text-[10px] text-amber-500 font-medium tracking-widest">INTELLIGENCE NETWORK</span>
              </div>
            )}
          </div>
          
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="hidden md:flex rounded-lg p-1.5 text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          >
            <Menu className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-4 px-3 py-4 overflow-y-auto overflow-x-hidden">
          {navGroups.map((group, idx) => (
            <div key={idx} className="flex flex-col gap-1">
              {isSidebarOpen && (
                <div className="px-3 pb-1 pt-2">
                  <span className="text-[10px] font-bold tracking-widest text-muted-foreground uppercase">{group.group}</span>
                </div>
              )}
              {group.items.map((item) => {
                const isActive = pathname.startsWith(item.href) && item.href !== "/dashboard" || pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center gap-3.5 px-3 py-2.5 rounded-md text-sm font-medium transition-all group duration-200 ${
                      isActive 
                        ? "bg-primary/10 border-l-2 border-primary text-primary shadow-sm" 
                        : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground border-l-2 border-transparent"
                    }`}
                  >
                    <Icon className={`h-4 w-4 shrink-0 transition-transform group-hover:scale-105 ${
                      isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                    }`} />
                    {isSidebarOpen && <span className="truncate">{item.name}</span>}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* User profile & Logout footer */}
        <div className="border-t border-border p-4">
          {isSidebarOpen ? (
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/20 border border-primary/30 text-primary">
                  <User className="h-4 w-4" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-semibold text-foreground truncate">{user?.first_name} {user?.last_name}</span>
                  <span className="text-[10px] text-muted-foreground truncate">Badge: {user?.badge_number}</span>
                </div>
              </div>
              
              <button 
                onClick={() => logout()}
                className="flex w-full items-center justify-center gap-2 px-3 py-2 rounded-md bg-secondary hover:bg-destructive/10 hover:text-destructive border border-border text-xs font-semibold text-muted-foreground transition-all"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Secure Log Out</span>
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <button 
                onClick={() => logout()}
                className="flex h-9 w-9 items-center justify-center rounded-md bg-secondary hover:bg-destructive/10 hover:text-destructive border border-border text-muted-foreground transition-all"
                title="Secure Log Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Container */}
      <div className={`flex flex-col flex-1 min-h-screen transition-all duration-300 ${
        isSidebarOpen ? "md:pl-64" : "md:pl-20"
      }`}>
        
        <IntelligenceFeedTicker />

        {/* Top Navbar */}
        <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between px-6 border-b border-border bg-background/95 backdrop-blur-md">
          {/* Left info */}
          <div className="hidden lg:flex items-center gap-3">
            <div className="flex items-center gap-1.5 rounded-full bg-secondary border border-border px-3 py-1 text-[10px] font-semibold text-muted-foreground">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
              </span>
              <span>LINKRA SECURE PORTAL</span>
            </div>
            
            <div className="hidden sm:flex items-center gap-1.5 rounded-full bg-primary/10 border border-primary/20 px-3 py-1 text-[10px] font-semibold text-primary uppercase tracking-wider">
              <Lock className="h-3 w-3" />
              <span>ROLE: {user?.role || "OFFICER"}</span>
            </div>
          </div>

          <GlobalSearchBar />

          {/* Right actions */}
          <div className="flex items-center gap-4">
            
            {/* Language Toggle */}
            <div className="flex items-center rounded-md bg-secondary border border-border p-0.5 text-xs font-semibold">
              <button 
                onClick={() => setLanguage("EN")}
                className={`px-2 py-1 rounded-sm transition-all ${
                  language === "EN" ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                EN
              </button>
              <button 
                onClick={() => setLanguage("KA")}
                className={`px-2 py-1 rounded-sm transition-all ${
                  language === "KA" ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                ಕನ್ನಡ
              </button>
            </div>

            {/* Notifications */}
            <button className="relative flex h-8 w-8 items-center justify-center rounded-md bg-secondary border border-border text-muted-foreground hover:text-foreground hover:bg-secondary/80 transition-colors">
              <Bell className="h-4 w-4" />
              {notificationsCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[9px] font-bold text-destructive-foreground ring-2 ring-background">
                  {notificationsCount}
                </span>
              )}
            </button>

            {/* Security Mark */}
            <div className="hidden md:flex flex-col items-end">
              <span className="text-[10px] font-bold tracking-wider text-destructive bg-destructive/10 border border-destructive/20 px-2 py-0.5 rounded uppercase">
                CONFIDENTIAL
              </span>
              <span className="text-[8px] text-muted-foreground font-mono mt-0.5">IP: 10.168.4.12</span>
            </div>
          </div>
        </header>

        {/* Content Viewport */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
