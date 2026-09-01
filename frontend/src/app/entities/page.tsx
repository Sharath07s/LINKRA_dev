import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';

export default function EntitiesPage() {
  return (
    <DashboardLayout>
      <div className="flex flex-col items-center justify-center h-full min-h-[500px]">
        <h1 className="text-2xl font-bold mb-4">Entity Management</h1>
        <p className="text-gray-500">
          This feature is part of the SIH26189 architecture but is <strong>NOT YET IMPLEMENTED</strong>.
        </p>
      </div>
    </DashboardLayout>
  );
}
