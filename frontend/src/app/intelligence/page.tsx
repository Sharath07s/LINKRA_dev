"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/ui/empty-state";
import { Radar, Users, AlertTriangle, Shield } from "lucide-react";

export default function IntelligencePage() {
  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Intelligence Fusion</h1>
            <p className="text-muted-foreground mt-1">Cross-case intelligence, influencers, and anomalies.</p>
          </div>
        </div>

        <Tabs defaultValue="influencers" className="w-full">
          <TabsList className="bg-secondary/50 border border-border mb-4 h-12 p-1">
            <TabsTrigger value="influencers" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">
              <Users className="h-4 w-4 mr-2" />
              Influencers
            </TabsTrigger>
            <TabsTrigger value="anomalies" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Anomalies
            </TabsTrigger>
            <TabsTrigger value="potential-links" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">
              <Shield className="h-4 w-4 mr-2" />
              Potential Links
            </TabsTrigger>
          </TabsList>

          <TabsContent value="influencers" className="mt-0 outline-none">
            <EmptyState 
              icon={<Users className="h-10 w-10 text-muted-foreground" />}
              title="No Influencer Intelligence" 
              description="Influencer data will appear here once the intelligence engine identifies key nodes in the network." 
            />
          </TabsContent>

          <TabsContent value="anomalies" className="mt-0 outline-none">
            <EmptyState 
              icon={<AlertTriangle className="h-10 w-10 text-muted-foreground" />}
              title="No Anomalies Detected" 
              description="No suspicious patterns or behavioral anomalies have been detected across active investigations." 
            />
          </TabsContent>

          <TabsContent value="potential-links" className="mt-0 outline-none">
            <EmptyState 
              icon={<Shield className="h-10 w-10 text-muted-foreground" />}
              title="No Potential Links" 
              description="No hidden relationships or predicted links have been identified between entities yet." 
            />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
