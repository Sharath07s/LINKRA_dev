"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Plus, Filter, ArrowRight } from "lucide-react";
import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCrimes } from "@/hooks/useCrimes";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { EmptyState } from "@/components/ui/empty-state";

export default function InvestigationsPage() {
  const { data: crimes, isLoading, error } = useCrimes();
  const crimesList = crimes || [];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Active Investigations</h1>
            <p className="text-muted-foreground mt-1">Manage and track ongoing intelligence operations.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="bg-background border-border text-foreground hover:bg-secondary">
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <Plus className="mr-2 h-4 w-4" />
              New Case
            </Button>
          </div>
        </div>

        <Card className="bg-card border-border shadow-sm">
          <CardHeader className="pb-3 border-b border-border/50">
            <div className="flex flex-col sm:flex-row justify-between gap-4">
              <CardTitle className="text-lg font-semibold flex items-center text-foreground">
                All Cases
                <Badge variant="secondary" className="ml-3 bg-secondary text-foreground border border-border">
                  {isLoading ? "-" : crimesList.length}
                </Badge>
              </CardTitle>
              <div className="relative max-w-sm w-full">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input 
                  type="text" 
                  placeholder="Search case ID, title, or assignee..." 
                  className="pl-9 bg-background border-border focus:border-primary text-foreground"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-8">
                <LoadingState message="Loading investigations data..." />
              </div>
            ) : error ? (
              <div className="p-8">
                <ErrorState title="Failed to load investigations" description="Could not fetch data from the intelligence database." />
              </div>
            ) : crimesList.length === 0 ? (
              <div className="p-8">
                <EmptyState title="No Investigations Found" description="There are no active intelligence operations at this time." />
              </div>
            ) : (
              <Table>
                <TableHeader className="bg-secondary/30">
                  <TableRow className="border-border/50 hover:bg-transparent">
                    <TableHead className="text-muted-foreground font-medium">Case ID (FIR)</TableHead>
                    <TableHead className="text-muted-foreground font-medium">Title</TableHead>
                    <TableHead className="text-muted-foreground font-medium">Priority</TableHead>
                    <TableHead className="text-muted-foreground font-medium">Status</TableHead>
                    <TableHead className="text-muted-foreground font-medium">District</TableHead>
                    <TableHead className="text-muted-foreground font-medium">Date</TableHead>
                    <TableHead className="text-right text-muted-foreground font-medium">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {crimesList.map((inv: any) => (
                    <TableRow key={inv.id} className="border-border/50 hover:bg-secondary/50 transition-colors">
                      <TableCell className="font-mono font-medium text-primary">
                        <Link href={`/investigations/${inv.id}`} className="hover:text-primary/80 underline decoration-primary/30 underline-offset-4">
                          {inv.fir_number}
                        </Link>
                      </TableCell>
                      <TableCell className="text-foreground font-semibold">{inv.title}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={`
                          ${inv.severity === 'High' ? 'border-destructive/30 text-destructive bg-destructive/10' : ''}
                          ${inv.severity === 'Medium' ? 'border-amber-500/30 text-amber-500 bg-amber-500/10' : ''}
                          ${inv.severity === 'Low' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' : ''}
                        `}>
                          {inv.severity || "UNKNOWN"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className={`h-2 w-2 rounded-full ${inv.status === 'Under Investigation' ? 'bg-primary animate-pulse' : inv.status === 'FIR Registered' ? 'bg-amber-500' : 'bg-muted-foreground'}`} />
                          <span className="text-foreground text-xs font-medium">{inv.status}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">{inv.district}</TableCell>
                      <TableCell className="text-muted-foreground text-sm font-mono">{inv.date}</TableCell>
                      <TableCell className="text-right">
                        <Link href={`/investigations/${inv.id}`} className="inline-flex items-center justify-center h-8 px-3 text-sm font-medium rounded-md text-primary hover:bg-primary/10 transition-colors">
                          Open <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
