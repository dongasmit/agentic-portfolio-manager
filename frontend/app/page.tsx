"use client";

import { useEffect, useState } from "react";
import { TrendingUp, Wallet, PieChart, Activity, Send } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const chartData = [
  { month: "Jan", value: 53000 },
  { month: "Feb", value: 54500 },
  { month: "Mar", value: 58000 },
  { month: "Apr", value: 57200 },
  { month: "May", value: 61000 },
  { month: "Jun", value: 63000 },
];

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // AI Chat States
  const [query, setQuery] = useState("");
  const [aiResponse, setAiResponse] = useState("Agent standby. Ask a question about the portfolio's compliance.");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch(
          "https://agentic-portfolio-manager.onrender.com/api/metrics/returns/11111111-1111-1111-1111-111111111111"
        );
        const data = await res.json();
        if (data.status === "success") {
          setMetrics(data.metrics);
        }
      } catch (error) {
        console.error("Failed to fetch metrics", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const handleAnalyze = async () => {
    if (!query.trim()) return;
    
    setIsAnalyzing(true);
    setAiResponse("Agent is analyzing portfolio and compliance rules...");
    
    try {
      const res = await fetch("https://agentic-portfolio-manager.onrender.com/api/ai/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });
      const data = await res.json();
      setAiResponse(data.ai_response);
    } catch (error) {
      setAiResponse("Error connecting to the AI Agent. Ensure your FastAPI server is running.");
    } finally {
      setIsAnalyzing(false);
      setQuery(""); // Clear input
    }
  };

  if (loading) return <div className="p-10 text-white flex items-center justify-center min-h-screen">Loading Engine...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold">Client Portfolio Overview</h1>
          <p className="text-slate-400 mt-1">Smit Donga • Aggressive Risk Profile</p>
        </header>

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card title="Total Invested" value={`₹${metrics?.total_invested.toLocaleString()}`} icon={<Wallet className="text-blue-400" />} />
          <Card title="Current Value" value={`₹${metrics?.current_value.toLocaleString()}`} icon={<PieChart className="text-purple-400" />} />
          <Card title="Absolute Return" value={`${metrics?.absolute_return_percent}%`} icon={<TrendingUp className="text-emerald-400" />} trend="up" />
          <Card title="XIRR (Annualized)" value={`${metrics?.xirr_percent}%`} icon={<Activity className="text-amber-400" />} trend="up" />
        </div>

        {/* Chart Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-[400px] mb-8">
          <h2 className="text-lg font-semibold mb-6">Equity Curve (YTD)</h2>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" />
              <YAxis stroke="#64748b" domain={['auto', 'auto']} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '8px' }} itemStyle={{ color: '#38bdf8' }} />
              <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={3} dot={{ r: 4, fill: "#38bdf8" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* AI Agent Chat Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="text-indigo-400" /> Compliance AI Agent
          </h2>
          
          <div className="flex gap-4">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              disabled={isAnalyzing}
              placeholder="e.g., Review the current holdings. Are we violating any risk guidelines?" 
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 disabled:opacity-50"
            />
            <button 
              onClick={handleAnalyze}
              disabled={isAnalyzing || !query.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} /> Analyze
            </button>
          </div>
          
          <div className="mt-6 p-5 bg-slate-950 border border-slate-800 rounded-lg min-h-[120px] shadow-inner">
            <p className={`whitespace-pre-wrap leading-relaxed ${isAnalyzing ? 'text-indigo-400 animate-pulse' : 'text-slate-300'}`}>
              {aiResponse}
            </p>
          </div>
        </div>
        
      </div>
    </div>
  );
}

function Card({ title, value, icon, trend }: { title: string, value: string, icon: any, trend?: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
      <div className="flex justify-between items-center mb-4">
        <span className="text-sm font-medium text-slate-400">{title}</span>
        <div className="p-2 bg-slate-800/50 rounded-lg">{icon}</div>
      </div>
      <div className="flex items-baseline gap-2">
        <h3 className="text-2xl font-bold">{value}</h3>
      </div>
    </div>
  );
}