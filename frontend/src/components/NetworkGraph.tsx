import React, { useEffect, useRef, useState } from "react";
import { User, Phone, Car, FileText, Building2, MapPin, Calendar, Shield, Maximize, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";
import * as d3 from "d3";

interface NetworkGraphProps {
  nodes: any[];
  edges: any[];
  selectedNode: any;
  selectedEdge?: any;
  highlightedNodeIds: string[];
  onNodeClick: (node: any) => void;
  onEdgeClick?: (edge: any) => void;
  className?: string;
}

export default function NetworkGraph({ 
  nodes, 
  edges, 
  selectedNode,
  selectedEdge,
  highlightedNodeIds, 
  onNodeClick,
  onEdgeClick,
  className = ""
}: NetworkGraphProps) {
  const [coords, setCoords] = useState<Record<string, {x: number, y: number}>>({});
  const simulationRef = useRef<d3.Simulation<any, any> | null>(null);
  const simNodesRef = useRef<any[]>([]);
  const svgRef = useRef<SVGSVGElement>(null);
  const zoomGRef = useRef<SVGGElement>(null);
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

  // Initialize Zoom
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        d3.select(zoomGRef.current).attr("transform", event.transform.toString());
      });
      
    svg.call(zoom);
    zoomBehaviorRef.current = zoom;
    
    // Double click to zoom is disabled to prevent interference with node clicks
    svg.on("dblclick.zoom", null);
  }, []);

  // Initialize Force Simulation
  useEffect(() => {
    if (!nodes.length) {
      setCoords({});
      return;
    }
    
    const simNodes = nodes.map(n => ({ ...n }));
    const simEdges = edges.map(e => ({ ...e }));
    simNodesRef.current = simNodes;

    const simulation = d3.forceSimulation(simNodes)
      .force("link", d3.forceLink(simEdges).id((d: any) => d.id).distance(120))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(250, 175))
      .force("collide", d3.forceCollide().radius(40).iterations(2))
      .on("tick", () => {
         const newCoords: Record<string, {x: number, y: number}> = {};
         simNodes.forEach((n: any) => {
            newCoords[n.id] = {x: n.x, y: n.y};
         });
         setCoords({...newCoords});
      });
      
    simulationRef.current = simulation;
    return () => {
      simulation.stop();
    };
  }, [nodes, edges]);

  // Handle Dragging
  const handlePointerDown = (e: React.PointerEvent, nodeId: string) => {
    e.stopPropagation();
    const el = e.currentTarget;
    el.setPointerCapture(e.pointerId);
    
    const simNode = simNodesRef.current.find(n => n.id === nodeId);
    if (simNode && simulationRef.current) {
      simulationRef.current.alphaTarget(0.3).restart();
      simNode.fx = simNode.x;
      simNode.fy = simNode.y;
    }
  };

  const handlePointerMove = (e: React.PointerEvent, nodeId: string) => {
    if (e.buttons !== 1) return;
    e.stopPropagation();
    
    const simNode = simNodesRef.current.find(n => n.id === nodeId);
    if (simNode && zoomGRef.current) {
      const CTM = zoomGRef.current.getScreenCTM();
      if (CTM) {
        const x = (e.clientX - CTM.e) / CTM.a;
        const y = (e.clientY - CTM.f) / CTM.d;
        simNode.fx = x;
        simNode.fy = y;
      }
    }
  };

  const handlePointerUp = (e: React.PointerEvent, nodeId: string) => {
    e.stopPropagation();
    const el = e.currentTarget;
    el.releasePointerCapture(e.pointerId);
    
    const simNode = simNodesRef.current.find(n => n.id === nodeId);
    if (simNode && simulationRef.current) {
      simulationRef.current.alphaTarget(0);
    }
  };

  // Controls
  const handleResetLayout = () => {
    if (!simulationRef.current) return;
    simNodesRef.current.forEach(n => {
      n.fx = null;
      n.fy = null;
    });
    simulationRef.current.alpha(1).restart();
  };

  const handleFitGraph = () => {
    if (!svgRef.current || !zoomBehaviorRef.current || !simNodesRef.current.length) return;
    const svg = d3.select(svgRef.current);
    
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    simNodesRef.current.forEach(n => {
      if (n.x < minX) minX = n.x;
      if (n.y < minY) minY = n.y;
      if (n.x > maxX) maxX = n.x;
      if (n.y > maxY) maxY = n.y;
    });
    
    const width = svgRef.current.clientWidth || 500;
    const height = svgRef.current.clientHeight || 350;
    
    const dx = maxX - minX;
    const dy = maxY - minY;
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    
    const scale = Math.max(0.1, Math.min(2, 0.9 / Math.max(dx / width, dy / height)));
    const translate = [width / 2 - scale * cx, height / 2 - scale * cy];
    
    svg.transition().duration(750).call(
      zoomBehaviorRef.current.transform, 
      d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
    );
  };
  
  const handleZoom = (direction: "in" | "out") => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.transition().duration(300).call(
      direction === "in" ? zoomBehaviorRef.current.scaleBy : zoomBehaviorRef.current.scaleBy, 
      direction === "in" ? 1.3 : 0.7
    );
  };

  const getNodeColorClass = (type: string, isHighlighted: boolean, isSelected: boolean) => {
    if (highlightedNodeIds.length > 0 && !isHighlighted) {
      return "fill-slate-900 stroke-slate-800 opacity-20";
    }
    let fill = "", stroke = "";
    switch (type) {
      case "person": fill = "fill-blue-900/60"; stroke = "stroke-blue-400"; break;
      case "crime": fill = "fill-red-900/60"; stroke = "stroke-red-500"; break;
      case "phone": case "phonenumber": fill = "fill-purple-900/60"; stroke = "stroke-purple-400"; break;
      case "vehicle": fill = "fill-amber-900/60"; stroke = "stroke-amber-400"; break;
      case "organization": fill = "fill-emerald-900/60"; stroke = "stroke-emerald-400"; break;
      case "location": fill = "fill-teal-900/60"; stroke = "stroke-teal-400"; break;
      case "police_station": fill = "fill-indigo-900/60"; stroke = "stroke-indigo-400"; break;
      default: fill = "fill-slate-900"; stroke = "stroke-slate-400";
    }
    if (isSelected) stroke = `${stroke} stroke-[3.5px] drop-shadow-[0_0_8px_rgba(59,130,246,0.6)]`;
    return `${fill} ${stroke}`;
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case "crime": return FileText;
      case "phone": case "phonenumber": return Phone;
      case "vehicle": return Car;
      case "organization": return Building2;
      case "location": return MapPin;
      case "date": return Calendar;
      case "police_station": return Shield;
      default: return User;
    }
  };

  const getEdgeStyle = (edge: any) => {
    const isEdgeHighlighted = highlightedNodeIds.includes(edge.source) && highlightedNodeIds.includes(edge.target);
    const isSelected = selectedEdge?.id === edge.id ||
      (selectedEdge?.source === edge.source && selectedEdge?.target === edge.target && selectedEdge?.relation === edge.relation);

    if (isSelected) return "stroke-yellow-400 stroke-[2.5px] opacity-100";
    if (highlightedNodeIds.length > 0 && !isEdgeHighlighted) return "stroke-slate-900 opacity-15";
    
    if (isEdgeHighlighted) {
      if (edge.status === "PREDICTED") return "stroke-purple-500 stroke-[1.8px] opacity-80 [stroke-dasharray:4_4]";
      if (edge.status === "INFERRED") return "stroke-orange-500 stroke-[1.8px] opacity-80 [stroke-dasharray:2_2]";
      return "stroke-blue-500 stroke-[1.8px] opacity-80";
    }

    if (edge.status === "PREDICTED") return "stroke-purple-800 stroke-[1px] opacity-60 [stroke-dasharray:4_4]";
    if (edge.status === "INFERRED") return "stroke-orange-800 stroke-[1px] opacity-60 [stroke-dasharray:2_2]";
    return "stroke-slate-800 stroke-[1px] opacity-40";
  };

  return (
    <div className={`relative overflow-hidden w-full h-full flex flex-col ${className}`}>
      <div className="absolute inset-0 bg-[radial-gradient(#081730_1px,transparent_1px)] [background-size:2rem_2rem] opacity-35" />

      <div className="absolute right-4 bottom-4 z-20 flex flex-col gap-2 bg-[#050505]/80 p-2 rounded-xl border border-[#222222] backdrop-blur">
        <button onClick={() => handleZoom('in')} className="p-2 hover:bg-[#111] rounded-lg text-slate-400 hover:text-white transition" title="Zoom In">
          <ZoomIn className="h-4 w-4" />
        </button>
        <button onClick={() => handleZoom('out')} className="p-2 hover:bg-[#111] rounded-lg text-slate-400 hover:text-white transition" title="Zoom Out">
          <ZoomOut className="h-4 w-4" />
        </button>
        <div className="h-px bg-[#222] w-full my-1"></div>
        <button onClick={handleFitGraph} className="p-2 hover:bg-[#111] rounded-lg text-slate-400 hover:text-white transition" title="Fit to Screen">
          <Maximize className="h-4 w-4" />
        </button>
        <button onClick={handleResetLayout} className="p-2 hover:bg-[#111] rounded-lg text-slate-400 hover:text-white transition" title="Reset Layout">
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>

      <svg 
        ref={svgRef}
        className="w-full h-full min-h-[420px] z-10 select-none cursor-grab active:cursor-grabbing"
      >
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" className="fill-slate-500" />
          </marker>
        </defs>

        <g ref={zoomGRef}>
          {edges?.map((edge, idx) => {
            const start = coords[edge.source];
            const end = coords[edge.target];
            if (!start || !end) return null;

            const midX = (start.x + end.x) / 2;
            const midY = (start.y + end.y) / 2;
            const isEdgeHighlighted = highlightedNodeIds.includes(edge.source) && highlightedNodeIds.includes(edge.target);

            return (
              <g key={`edge-${idx}`} className={onEdgeClick ? "cursor-pointer" : ""}>
                <line
                  x1={start.x} y1={start.y}
                  x2={end.x} y2={end.y}
                  stroke="transparent"
                  strokeWidth="12"
                  onClick={(e) => { e.stopPropagation(); if(onEdgeClick) onEdgeClick(edge); }}
                />
                <line
                  x1={start.x} y1={start.y}
                  x2={end.x} y2={end.y}
                  className={`transition-all duration-300 ${getEdgeStyle(edge)}`}
                  markerEnd="url(#arrow)"
                />
                {(isEdgeHighlighted || selectedEdge?.source === edge.source) && (
                  <>
                    <rect
                      x={midX - 22} y={midY - 7} width="44" height="14" rx="3"
                      className="fill-slate-950 stroke-slate-700 stroke-[0.5px] opacity-90"
                    />
                    <text
                      x={midX} y={midY + 3.5} textAnchor="middle"
                      className="text-[5px] font-bold fill-slate-300 font-mono"
                    >
                      {edge.relation}
                    </text>
                  </>
                )}
              </g>
            );
          })}

          {nodes?.map((node) => {
            const coord = coords[node.id];
            if (!coord) return null;
            
            const isSelected = selectedNode?.id === node.id;
            const isHighlighted = highlightedNodeIds.includes(node.id);
            const Icon = getNodeIcon(node.type);

            return (
              <g 
                key={node.id} 
                transform={`translate(${coord.x}, ${coord.y})`}
                className="cursor-pointer node-group touch-none"
                onPointerDown={(e) => handlePointerDown(e, node.id)}
                onPointerMove={(e) => handlePointerMove(e, node.id)}
                onPointerUp={(e) => handlePointerUp(e, node.id)}
                onPointerCancel={(e) => handlePointerUp(e, node.id)}
                onClick={(e) => { e.stopPropagation(); onNodeClick(node); }}
              >
                {isSelected && (
                  <circle r="16" className="fill-[#10B981]/10 stroke-blue-500/30 stroke-[2.5px] animate-ping opacity-75 pointer-events-none" />
                )}
                
                <circle
                  r="12"
                  className={`transition-all duration-300 ${getNodeColorClass(node.type, isHighlighted, isSelected)}`}
                />

                <g transform="translate(-5, -5)" className={`${
                  highlightedNodeIds.length > 0 && !isHighlighted ? "opacity-20" : "opacity-90"
                } pointer-events-none`}>
                  <Icon className="h-2.5 w-2.5 text-white" strokeWidth={2.5} />
                </g>

                <text
                  y="22"
                  textAnchor="middle"
                  className={`text-[7px] font-bold font-sans tracking-wide transition-all pointer-events-none ${
                    isSelected 
                      ? "fill-blue-400 text-xs font-extrabold" 
                      : highlightedNodeIds.length > 0 && !isHighlighted 
                      ? "fill-slate-650 opacity-20" 
                      : "fill-slate-200"
                  }`}
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
