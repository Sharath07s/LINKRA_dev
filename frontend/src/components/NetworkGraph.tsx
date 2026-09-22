import React from "react";
import { User, Phone, Car, FileText, Building2, MapPin, Calendar, Shield } from "lucide-react";

interface NetworkGraphProps {
  nodes: any[];
  edges: any[];
  nodeCoordinates: Record<string, {x: number, y: number}>;
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
  nodeCoordinates, 
  selectedNode,
  selectedEdge,
  highlightedNodeIds, 
  onNodeClick,
  onEdgeClick,
  className = ""
}: NetworkGraphProps) {

  // Map backend node types (from Neo4j labels) to display types
  // Backend emits: person, organization, location, vehicle, phone, date, crime, police_station
  const getNodeColorClass = (type: string, isHighlighted: boolean, isSelected: boolean) => {
    if (highlightedNodeIds.length > 0 && !isHighlighted) {
      return "fill-slate-900 stroke-slate-800 opacity-20";
    }

    let fill = "";
    let stroke = "";
    
    switch (type) {
      case "person":
        fill = "fill-blue-900/60";
        stroke = "stroke-blue-400";
        break;
      case "crime":
        fill = "fill-red-900/60";
        stroke = "stroke-red-500";
        break;
      case "phone":
      case "phonenumber":
        fill = "fill-purple-900/60";
        stroke = "stroke-purple-400";
        break;
      case "vehicle":
        fill = "fill-amber-900/60";
        stroke = "stroke-amber-400";
        break;
      case "organization":
        fill = "fill-emerald-900/60";
        stroke = "stroke-emerald-400";
        break;
      case "location":
        fill = "fill-teal-900/60";
        stroke = "stroke-teal-400";
        break;
      case "police_station":
        fill = "fill-indigo-900/60";
        stroke = "stroke-indigo-400";
        break;
      default:
        fill = "fill-slate-900";
        stroke = "stroke-slate-400";
    }

    if (isSelected) {
      stroke = `${stroke} stroke-[3.5px] drop-shadow-[0_0_8px_rgba(59,130,246,0.6)]`;
    }

    return `${fill} ${stroke}`;
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case "crime": return FileText;
      case "phone":
      case "phonenumber": return Phone;
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

    if (isSelected) {
      return "stroke-yellow-400 stroke-[2.5px] opacity-100";
    }

    if (highlightedNodeIds.length > 0 && !isEdgeHighlighted) {
      return "stroke-slate-900 opacity-15";
    }

    if (isEdgeHighlighted) {
      if (edge.status === "PREDICTED") return "stroke-purple-500 stroke-[1.8px] opacity-80 [stroke-dasharray:4_4]";
      if (edge.status === "INFERRED") return "stroke-orange-500 stroke-[1.8px] opacity-80 [stroke-dasharray:2_2]";
      return "stroke-blue-500 stroke-[1.8px] opacity-80";
    }

    if (edge.status === "PREDICTED") return "stroke-purple-800 stroke-[1px] opacity-60 [stroke-dasharray:4_4]";
    if (edge.status === "INFERRED") return "stroke-orange-800 stroke-[1px] opacity-60 [stroke-dasharray:2_2]";
    return "stroke-slate-800 stroke-[1px] opacity-40";
  };

  const handleEdgeClick = (edge: any, event: React.MouseEvent) => {
    event.stopPropagation();
    if (onEdgeClick) onEdgeClick(edge);
  };

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Background constellation overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(#081730_1px,transparent_1px)] [background-size:2rem_2rem] opacity-35" />

      {/* SVG Network Graph */}
      <svg 
        className="w-full max-w-2xl h-[420px] z-10 select-none mx-auto"
        viewBox="0 0 500 350"
      >
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="15" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" className="fill-slate-850" />
          </marker>
        </defs>

        {/* Draw Edges */}
        {edges?.map((edge, idx) => {
          const start = nodeCoordinates[edge.source];
          const end = nodeCoordinates[edge.target];
          if (!start || !end) return null;

          const midX = (start.x + end.x) / 2;
          const midY = (start.y + end.y) / 2;
          const isEdgeHighlighted = highlightedNodeIds.includes(edge.source) && highlightedNodeIds.includes(edge.target);

          return (
            <g key={`edge-${idx}`} className={onEdgeClick ? "cursor-pointer" : ""}>
              {/* Wider invisible hit area for easier clicking */}
              <line
                x1={start.x} y1={start.y}
                x2={end.x} y2={end.y}
                stroke="transparent"
                strokeWidth="12"
                onClick={(e) => handleEdgeClick(edge, e)}
              />
              {/* Visible edge line */}
              <line
                x1={start.x}
                y1={start.y}
                x2={end.x}
                y2={end.y}
                className={`transition-all duration-300 ${getEdgeStyle(edge)}`}
                onClick={(e) => handleEdgeClick(edge, e)}
              />
              {/* Edge label (shown when highlighted or selected) */}
              {(isEdgeHighlighted || selectedEdge?.source === edge.source) && (
                <>
                  <rect
                    x={midX - 22}
                    y={midY - 7}
                    width="44"
                    height="14"
                    rx="3"
                    className="fill-slate-950 stroke-slate-700 stroke-[0.5px] opacity-90"
                  />
                  <text
                    x={midX}
                    y={midY + 3.5}
                    textAnchor="middle"
                    className="text-[5px] font-bold fill-slate-300 font-mono"
                  >
                    {edge.relation}
                  </text>
                </>
              )}
            </g>
          );
        })}

        {/* Draw Nodes */}
        {nodes?.map((node) => {
          const coord = nodeCoordinates[node.id];
          if (!coord) return null;
          
          const isSelected = selectedNode?.id === node.id;
          const isHighlighted = highlightedNodeIds.includes(node.id);
          const Icon = getNodeIcon(node.type);

          return (
            <g 
              key={node.id} 
              transform={`translate(${coord.x}, ${coord.y})`}
              className="cursor-pointer"
              onClick={() => onNodeClick(node)}
            >
              {/* Ring highlight glow */}
              {isSelected && (
                <circle r="16" className="fill-[#10B981]/10 stroke-blue-500/30 stroke-[2.5px] animate-ping opacity-75" />
              )}
              
              {/* Node circle */}
              <circle
                r="12"
                className={`transition-all duration-300 ${getNodeColorClass(node.type, isHighlighted, isSelected)}`}
              />

              {/* Node Icon inside */}
              <g transform="translate(-5, -5)" className={`${
                highlightedNodeIds.length > 0 && !isHighlighted ? "opacity-20" : "opacity-90"
              }`}>
                <Icon className="h-2.5 w-2.5 text-white" strokeWidth={2.5} />
              </g>

              {/* Text Label */}
              <text
                y="20"
                textAnchor="middle"
                className={`text-[6px] font-bold font-sans tracking-wide transition-all ${
                  isSelected 
                    ? "fill-blue-400 text-xs font-extrabold" 
                    : highlightedNodeIds.length > 0 && !isHighlighted 
                    ? "fill-slate-650 opacity-20" 
                    : "fill-slate-300"
                }`}
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
