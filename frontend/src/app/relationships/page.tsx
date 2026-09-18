'use client';

import React, { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { relationshipService, EntityRelationship } from '@/services/relationship.service';

export default function RelationshipExplorer() {
  const [entityId, setEntityId] = useState('');
  const [relationships, setRelationships] = useState<EntityRelationship[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRelationships = async () => {
    if (!entityId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await relationshipService.getEntityRelationships(entityId);
      setRelationships(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch relationships');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Relationship Explorer</h1>
            <p className="text-gray-400 mt-2">M1.6 Evidence-Based Relationship Discovery Layer</p>
          </div>
        </div>

        <Card className="bg-[#1C1F26] border-gray-800">
          <CardHeader>
            <CardTitle className="text-gray-200">Query Relationships by Canonical Entity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                placeholder="Enter Canonical Entity UUID"
                value={entityId}
                onChange={(e) => setEntityId(e.target.value)}
                className="bg-[#0B0D11] border-gray-800 text-white w-96"
              />
              <Button onClick={fetchRelationships} disabled={loading || !entityId} className="bg-[#10B981] hover:bg-blue-700">
                {loading ? 'Querying...' : 'Fetch Links'}
              </Button>
            </div>
            
            {error && <div className="mt-4 p-4 bg-red-900/20 border border-red-900 rounded text-red-400">{error}</div>}

            {relationships.length > 0 && (
              <div className="mt-8 overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-400">
                  <thead className="text-xs uppercase bg-[#252A33] text-gray-300">
                    <tr>
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Extraction Method</th>
                      <th className="px-4 py-3">Job ID</th>
                      <th className="px-4 py-3">Source Row/Page</th>
                    </tr>
                  </thead>
                  <tbody>
                    {relationships.map((rel) => (
                      <tr key={rel.id} className="border-b border-gray-800 hover:bg-[#2A2F3A] transition-colors">
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-900/30 text-[#10B981] border border-blue-800">
                            {rel.relationship_type}
                          </span>
                        </td>
                        <td className="px-4 py-3">{(rel.confidence * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3">{rel.extraction_method}</td>
                        <td className="px-4 py-3 text-xs">{rel.ingestion_job_id}</td>
                        <td className="px-4 py-3">{rel.source_row || rel.source_page || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {!loading && relationships.length === 0 && entityId && !error && (
               <div className="mt-8 text-center text-gray-500 py-8 border border-dashed border-gray-700 rounded-lg">
                 No relationships discovered for this entity yet.
               </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
