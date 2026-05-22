import { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BrainCircuit, Users, MapPin, CloudLightning, Cpu, Save, CheckCircle, Server, Radar, Zap, BarChart3 } from 'lucide-react';

function App() {
  const [simData, setSimData] = useState(null);
  const [history, setHistory] = useState([]); 
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState("");

  const aldeas = ["Suchitán", "El Limón", "Buena Vista"];

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date().toLocaleString('es-GT', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/simulate');
      const data = response.data;
      setSimData(data);
      const recompensaGlobal = data.recompensas_obtenidas.reduce((a, b) => a + b, 0);
      setHistory(prev => [...prev, { episodio: data.episodio, recompensa: recompensaGlobal, emergencias: data.estado_actual.emergencias_activas }]);
    } catch (error) { console.error(error); }
    setLoading(false);
  };

  const triggerChaos = async () => {
    setLoading(true);
    try {
      await axios.get('http://127.0.0.1:8000/api/force_chaos');
      await runSimulation(); 
    } catch (error) { console.error(error); }
    setLoading(false);
  };

  const recursos = simData ? simData.estado_actual.recursos : 100;
  const radio = 70;
  const offset = (2 * Math.PI * radio) - (recursos / 100) * (2 * Math.PI * radio);

  const epsilon = simData?.tasa_exploracion || 1.0;
  const exploracionPct = (epsilon * 100).toFixed(1);
  const conocimientoPct = (100 - exploracionPct).toFixed(1);

  return (
    <div className="min-h-screen bg-[#181A1F] text-slate-300 p-6 font-sans">
      <header className="mb-6 flex justify-between items-start border-b border-teal-800/30 pb-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2 text-teal-400">
            <BrainCircuit size={28} /> CoreRL Suite
          </h1>
          <p className="text-slate-500 text-sm mt-1">Coordinación Logística Autónoma - Santa Catarina Mita</p>
          {simData?.cerebro_cargado && (
            <span className="inline-flex items-center gap-1 mt-2 text-xs text-green-400 bg-green-900/20 border border-green-500/30 px-2 py-0.5 rounded">
              <Save size={12} /> Red Neuronal Target Cargada
            </span>
          )}
        </div>
        
        {/* PANEL DERECHO: MÉTRICAS Y CONTROLES */}
        <div className="flex items-center gap-4">
          
          {/* Panel de AutoML (Aparece tras 20 turnos) */}
          {simData?.ml_metrics && simData.ml_metrics.best_model_name !== "Ninguno" && (
            <div className="bg-[#21252B] border border-slate-700 p-2 rounded text-[11px] font-mono shadow-md hidden lg:block">
              <p className="text-blue-400 font-bold mb-1 flex items-center gap-1"><BarChart3 size={12}/> AutoML Report ({simData.ml_metrics.best_model_name})</p>
              <div className="grid grid-cols-4 gap-3 text-center">
                <div><span className="text-slate-500 block text-[9px]">ACC</span><span className="text-white">{simData.ml_metrics.accuracy.toFixed(1)}%</span></div>
                <div><span className="text-slate-500 block text-[9px]">PREC</span><span className="text-white">{simData.ml_metrics.precision.toFixed(1)}%</span></div>
                <div><span className="text-slate-500 block text-[9px]">REC</span><span className="text-white">{simData.ml_metrics.recall.toFixed(1)}%</span></div>
                <div><span className="text-slate-500 block text-[9px]">F1</span><span className="text-white">{simData.ml_metrics.f1_score.toFixed(1)}%</span></div>
              </div>
            </div>
          )}

          {/* Bloque de Indicadores Dinámicos */}
          <div className="text-right hidden md:block">
            {/* Reloj del sistema */}
            <p className="text-teal-500 text-sm font-mono">{time}</p>
            
            {/* Riesgo Predicho */}
            {simData?.prediccion_riesgo && (
              <p className="text-orange-400 text-xs mt-1 border border-orange-500/30 bg-orange-500/10 px-2 py-0.5 rounded flex items-center justify-end gap-1">
                <BrainCircuit size={12} /> Riesgo: {simData.prediccion_riesgo}
              </p>
            )}
            
            {/* Pérdida de la Red Neuronal */}
            {simData && (
              <p className={`text-xs mt-1 border px-2 py-0.5 rounded flex items-center justify-end gap-1 transition-all ${simData.loss_neuronal > 0 ? 'text-purple-400 border-purple-500/50 bg-purple-500/10' : 'text-slate-500 border-slate-700 bg-slate-800'}`}>
                <Cpu size={12} /> {simData.loss_neuronal > 0 ? `Target Loss: ${simData.loss_neuronal.toFixed(4)}` : 'Llenando Replay...'}
              </p>
            )}

            {/* Meta-LR Dinámico */}
            {simData?.loss_neuronal > 0 && simData?.meta_learning_rate && (
              <p className="text-pink-400 text-[10px] mt-1 border border-pink-500/30 bg-pink-500/10 px-2 py-0.5 rounded flex items-center justify-end gap-1 shadow-[0_0_8px_rgba(236,72,153,0.15)] transition-all">
                <Zap size={10} /> Meta-LR: {simData.meta_learning_rate.toFixed(5)}
              </p>
            )}
          </div>

          {/* Botones de Control */}
          <button onClick={triggerChaos} disabled={loading} className="bg-red-900/20 hover:bg-red-600/40 text-red-400 border border-red-500/50 px-4 py-2 rounded font-mono text-sm transition-all flex items-center gap-2">
            <CloudLightning size={16} /> Tormenta
          </button>
          <button onClick={runSimulation} disabled={loading} className="bg-teal-600/10 hover:bg-teal-500/20 text-teal-400 border border-teal-500/50 px-6 py-2 rounded font-mono text-sm transition-all flex items-center gap-2">
            {loading ? "Procesando..." : "Siguiente Turno"} <Zap size={16} />
          </button>
        </div>
      </header>

      {/* RENDERIZADO DEL MAPA TOPOLÓGICO Y CONTROL */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <div className="lg:col-span-1 bg-[#21252B] rounded border-t-2 border-teal-500 p-6 shadow-lg flex flex-col justify-between">
          <div>
            <h2 className="text-teal-500/80 font-semibold text-sm mb-4">Suministros Centrales</h2>
            <div className="relative flex justify-center mb-6">
              <svg className="transform -rotate-90 w-36 h-36">
                <circle cx="72" cy="72" r={radio} stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-700" />
                <circle cx="72" cy="72" r={radio} stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray={2 * Math.PI * radio} strokeDashoffset={offset} className="text-teal-400 transition-all duration-1000 ease-out" />
              </svg>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                <span className="text-3xl font-bold text-white">{recursos}</span>
              </div>
            </div>
          </div>
          <div className="border-t border-slate-700 pt-4">
            <h3 className="text-xs text-slate-400 font-mono mb-2 flex justify-between">
              <span>Nivel de Conocimiento (DQN)</span>
              <span className="text-purple-400">{conocimientoPct}%</span>
            </h3>
            <div className="w-full bg-orange-500/20 rounded-full h-2.5 overflow-hidden flex">
              <div className="bg-purple-500 h-2.5 transition-all duration-500" style={{ width: `${conocimientoPct}%` }}></div>
              <div className="bg-orange-500 h-2.5 transition-all duration-500 opacity-50" style={{ width: `${exploracionPct}%` }}></div>
            </div>
            <div className="flex justify-between text-[10px] mt-1 font-mono">
              <span className="text-purple-400">Explotando</span>
              <span className="text-orange-400">Explorando</span>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 bg-[#21252B] rounded border-t-2 border-slate-600 p-4 shadow-lg flex flex-col relative overflow-hidden">
          <h2 className="text-slate-400 font-semibold text-sm mb-2 flex items-center gap-2 z-10 relative"><Radar size={16} /> Mapa de Nodos (Red Logística CoreRL)</h2>
          <div className="flex-1 relative mt-4 bg-[#181A1F] rounded-lg border border-slate-700/50">
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {[0, 1, 2].map((i) => {
                const accion = simData ? simData.acciones_ejecutadas[i] : null;
                const x2 = i === 0 ? "25%" : i === 1 ? "50%" : "75%";
                const y2 = i === 1 ? "25%" : "35%";
                let strokeColor = "#334155"; let isPulse = false; let strokeWidth = "2";
                if (accion === 1) { strokeColor = "#2dd4bf"; isPulse = true; strokeWidth = "4"; }
                if (accion === 2) { strokeColor = "#3b82f6"; isPulse = true; strokeWidth = "4"; }
                return <line key={i} x1="50%" y1="85%" x2={x2} y2={y2} stroke={strokeColor} strokeWidth={strokeWidth} className={`transition-all duration-500 ${isPulse ? 'animate-pulse drop-shadow-[0_0_8px_currentColor]' : ''}`} />;
              })}
            </svg>
            <div className="absolute left-1/2 bottom-[15%] transform -translate-x-1/2 translate-y-1/2 flex flex-col items-center">
              <div className="bg-slate-900 border-2 border-white p-3 rounded-full z-10 shadow-[0_0_15px_rgba(255,255,255,0.2)]"><Server className="text-white" size={24} /></div>
              <span className="text-xs font-bold text-white mt-1 bg-slate-900/80 px-2 py-0.5 rounded">Municipalidad</span>
            </div>
            {[0, 1, 2].map((i) => {
              const accion = simData ? simData.acciones_ejecutadas[i] : null;
              const recompensa = simData ? simData.recompensas_obtenidas[i] : 0;
              const leftPos = i === 0 ? "25%" : i === 1 ? "50%" : "75%";
              const topPos = i === 1 ? "25%" : "35%";
              let colorBorder = "border-slate-700 bg-slate-900"; let colorIcon = "text-slate-500"; let shadow = "";
              if (accion === 1) { colorBorder = "border-teal-500 bg-teal-900/30"; colorIcon = "text-teal-400"; shadow = "shadow-[0_0_15px_rgba(45,212,191,0.5)]"; }
              if (accion === 2) { colorBorder = "border-blue-500 bg-blue-900/30"; colorIcon = "text-blue-400"; shadow = "shadow-[0_0_15px_rgba(59,130,246,0.5)]"; }
              return (
                <div key={i} className="absolute transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center" style={{ left: leftPos, top: topPos }}>
                  <div className={`p-2 rounded-full border-2 z-10 transition-all duration-300 ${colorBorder} ${shadow}`}><MapPin className={colorIcon} size={20} /></div>
                  <span className="text-[11px] font-bold text-white mt-1 bg-slate-900/80 px-2 py-0.5 rounded">{aldeas[i]}</span>
                  {simData && <span className={`text-[10px] font-mono mt-1 ${recompensa >= 0 ? 'text-teal-400' : 'text-red-400'}`}>R: {recompensa}</span>}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* SECCIÓN DE HISTORIAL Y LOGS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <div className="lg:col-span-1 bg-[#21252B] rounded border-t-2 border-slate-600 shadow-lg overflow-hidden flex flex-col h-48">
          <div className="p-3 bg-[#181A1F] border-b border-slate-700/50"><h2 className="text-slate-400 font-semibold text-sm">Bitácora Lógica</h2></div>
          <div className="p-3 overflow-y-auto space-y-2 text-xs font-mono">
            {!simData && <p className="text-slate-600 italic">Esperando telemetría...</p>}
            {simData?.intervencion_logica.map((regla, index) => {
              const isIntervention = !regla.includes("Ninguna");
              return <div key={index} className={`p-1.5 rounded border-l-2 ${isIntervention ? 'border-orange-500 bg-orange-500/10 text-orange-200' : 'border-slate-600 bg-[#181A1F] text-slate-400'}`}>{regla}</div>
            })}
          </div>
        </div>
        <div className="lg:col-span-2 bg-[#21252B] rounded border-t-2 border-teal-500 p-4 shadow-lg h-48">
          <h2 className="text-teal-500/80 font-semibold text-sm mb-2">Estabilidad del Ecosistema</h2>
          {history.length > 0 ? (
            <ResponsiveContainer width="100%" height="80%">
              <AreaChart data={history} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                <defs><linearGradient id="colorRecompensa" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.3}/><stop offset="95%" stopColor="#2dd4bf" stopOpacity={0}/></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="episodio" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', fontSize: '12px' }} itemStyle={{ color: '#2dd4bf' }} />
                <Area type="monotone" dataKey="recompensa" stroke="#2dd4bf" strokeWidth={2} fillOpacity={1} fill="url(#colorRecompensa)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : <div className="h-full flex items-center justify-center text-slate-600 text-sm italic">Requiere telemetría...</div>}
        </div>
      </div>
    </div>
  );
}

export default App;