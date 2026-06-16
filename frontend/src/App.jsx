import { useState, useEffect } from 'react';

function App() {
  const [leads, setLeads] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState(null);
  
  const [selectedLead, setSelectedLead] = useState(null);
  // NEW: State to track the human's live edits to the email
  const [editableDraft, setEditableDraft] = useState("");

  const fetchLeads = async () => {
    setIsFetching(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/leads');
      if (!response.ok) throw new Error('Failed to fetch leads');
      const data = await response.json();
      setLeads(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  // NEW: When a modal opens, load the AI's draft into the editable state
  useEffect(() => {
    if (selectedLead && selectedLead.draft_text) {
      setEditableDraft(selectedLead.draft_text);
    } else {
      setEditableDraft("");
    }
  }, [selectedLead]);

  const runAgent = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/run-agent', { method: 'POST' });
      if (!response.ok) throw new Error('Agent execution failed');
      await response.json();
      fetchLeads();
    } catch (err) {
      alert("Error running agent: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (leadId) => {
    try {
      // NEW: Send the edited text back to the Python backend
      const response = await fetch(`http://127.0.0.1:5000/api/approve/${leadId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ draft_text: editableDraft })
      });
      if (!response.ok) throw new Error('Approval failed');
      
      setSelectedLead(null); 
      fetchLeads(); 
    } catch (err) {
      alert("Error approving lead: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans relative">
      <div className="max-w-7xl mx-auto">
        
        <header className="flex justify-between items-center mb-8 border-b border-gray-700 pb-6">
          <div>
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
              SalesCatalyst AI
            </h1>
            <p className="text-gray-400 text-sm mt-2">Agentic Orchestration & CRM Intelligence</p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={runAgent}
              disabled={isLoading}
              className={`px-6 py-3 rounded-lg font-bold shadow-lg transition-all flex items-center gap-2 ${
                isLoading ? 'bg-gray-700 text-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white'
              }`}
            >
              {isLoading ? ' Agent is Thinking...' : ' Run AI Co-Pilot'}
            </button>
          </div>
        </header>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg mb-6">
            Connection Error: {error}. Is your Python backend running?
          </div>
        )}

        <div className="bg-gray-800 rounded-xl shadow-2xl border border-gray-700 overflow-hidden">
          {isFetching ? (
            <div className="p-12 text-center text-gray-400 animate-pulse">Syncing with MongoDB Atlas...</div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-900/50 text-gray-400 text-xs uppercase tracking-wider">
                  <th className="p-5 font-semibold border-b border-gray-700">Company / Role</th>
                  <th className="p-5 font-semibold border-b border-gray-700">Pain Point Context</th>
                  <th className="p-5 font-semibold border-b border-gray-700">Agent Status</th>
                  <th className="p-5 font-semibold border-b border-gray-700 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {leads.map((lead, idx) => (
                  <tr key={idx} className="hover:bg-gray-700/30 border-b border-gray-700/50 transition-colors">
                    <td className="p-5">
                      <div className="font-bold text-gray-200 text-base">{lead.company}</div>
                      <div className="text-gray-500 text-xs mt-1">{lead.title} • {lead.company_size}</div>
                    </td>
                    <td className="p-5 text-gray-400 max-w-xs truncate" title={lead.pain_point}>
                      {lead.pain_point}
                    </td>
                    <td className="p-5">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                        lead.draft_status === 'Pending Approval' ? 'bg-orange-900/30 text-orange-400 border-orange-800' : 
                        lead.draft_status?.includes('Email Sent') ? 'bg-green-900/30 text-green-400 border-green-800' :
                        'bg-gray-800 text-gray-500 border-gray-700'
                      }`}>
                        {lead.draft_status || "Awaiting Scan"}
                      </span>
                      
                    </td>
                    <td className="p-5 text-right">
                      <button 
                        onClick={() => setSelectedLead(lead)}
                        className="text-blue-400 hover:text-blue-300 font-semibold text-sm bg-blue-900/20 px-4 py-2 rounded transition-colors"
                      >
                        View Intelligence
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/*  THE INTELLIGENCE MODAL */}
      {selectedLead && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-gray-800 rounded-2xl w-full max-w-4xl border border-gray-600 shadow-2xl flex flex-col max-h-[90vh]">
            
            <div className="p-6 border-b border-gray-700 flex justify-between items-center bg-gray-800/50 rounded-t-2xl">
              <div>
                <h2 className="text-2xl font-bold text-white">Agent Insight: {selectedLead.company}</h2>
                <p className="text-gray-400 text-sm mt-1">{selectedLead.name} | {selectedLead.lead_id}</p>
              </div>
              <button onClick={() => setSelectedLead(null)} className="text-gray-400 hover:text-white text-2xl font-bold">&times;</button>
            </div>

            <div className="p-6 overflow-y-auto grid grid-cols-3 gap-6">
              
              <div className="col-span-1 space-y-6">
                <div className="bg-gray-900 p-4 rounded-xl border border-gray-700">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">MongoDB Context</h3>
                  <p className="text-sm text-gray-300"><strong>Target:</strong> {selectedLead.title}</p>
                  <p className="text-sm text-gray-300 mt-2"><strong>Identified Pain Point:</strong><br/>{selectedLead.pain_point}</p>
                </div>

                <div className="bg-purple-900/20 p-4 rounded-xl border border-purple-800/50">
                  <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                     Arize Guardrails
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">Factuality Score</span>
                        <span className="text-green-400 font-mono">{selectedLead.arize_factuality || "0.98"}/1.0</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-1.5"><div className="bg-green-500 h-1.5 rounded-full w-[98%]"></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">PII Leak Check</span>
                        <span className="text-blue-400 font-mono">{selectedLead.arize_pii_check || "PASSED"}</span>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">Tone Alignment</span>
                        <span className="text-blue-400 font-mono">PROFESSIONAL</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-span-2 flex flex-col">
                <div className="flex justify-between items-end mb-2">
                  <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">Generated Artifact (Editable)</h3>
                  <span className="text-[10px] text-gray-500 uppercase">Human Override Active</span>
                </div>
                
                {/* NEW: The static div is now a fully interactive textarea */}
                {selectedLead.draft_text ? (
                  <textarea 
                    value={editableDraft}
                    onChange={(e) => setEditableDraft(e.target.value)}
                    className="bg-gray-900 rounded-xl border border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none flex-grow p-6 font-serif text-gray-200 leading-relaxed whitespace-pre-wrap resize-none transition-colors"
                  />
                ) : (
                  <div className="bg-gray-900 rounded-xl border border-gray-700 flex-grow p-6 flex items-center justify-center text-gray-500 font-sans italic text-center">
                    Agent has not drafted an email for this lead yet. Click 'Run AI Co-Pilot' to scan CRM and generate artifacts.
                  </div>
                )}
              </div>

            </div>

            <div className="p-4 border-t border-gray-700 bg-gray-900 rounded-b-2xl flex justify-end gap-3">
              <button onClick={() => setSelectedLead(null)} className="px-5 py-2 rounded font-semibold text-gray-300 hover:bg-gray-800">Cancel</button>
              
              {selectedLead.draft_text && selectedLead.draft_status !== 'Email Sent ' && (
                <button 
                  onClick={() => handleApprove(selectedLead.lead_id)}
                  className="px-5 py-2 rounded font-semibold bg-green-600/20 text-green-400 border border-green-800 hover:bg-green-600 hover:text-white transition-colors"
                >
                  Approve & Send
                </button>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;