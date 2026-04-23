import React, { useState } from "react";

interface Props { onComplete: () => void; }

const CHAINS = ["Solana", "Ethereum", "Base", "BSC", "Arbitrum"];
const INTERESTS = ["DeFi", "NFTs", "Meme Coins", "Trading", "Security", "Research"];

export default function OnboardingModal({ onComplete }: Props) {
  const [step, setStep] = useState(0);
  const [displayName, setDisplayName] = useState("");
  const [selectedChains, setSelectedChains] = useState<string[]>([]);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);

  const toggle = (item: string, list: string[], setList: (v: string[]) => void) => {
    setList(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
  };

  const submit = async () => {
    await fetch("/api/v1/me", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: displayName, chains: selectedChains, interests: selectedInterests, onboarding_completed: true }),
    });
    onComplete();
  };

  const steps = [
    <div key="0" className="text-center">
      <h2 className="text-2xl font-bold text-white mb-2">Welcome to RugMuncher 🛡️</h2>
      <p className="text-gray-400 mb-6">Crypto scam detection powered by AI</p>
      <button onClick={() => setStep(1)} className="bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-3 rounded-xl font-semibold">Get Started</button>
    </div>,
    <div key="1">
      <h2 className="text-xl font-bold text-white mb-4">What should we call you?</h2>
      <input className="w-full bg-gray-800 text-white p-4 rounded-xl mb-4" placeholder="Display name" value={displayName} onChange={e => setDisplayName(e.target.value)} />
      <button onClick={() => displayName && setStep(2)} className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg w-full" disabled={!displayName}>Next</button>
    </div>,
    <div key="2">
      <h2 className="text-xl font-bold text-white mb-4">Which chains do you track?</h2>
      <div className="grid grid-cols-2 gap-3 mb-4">
        {CHAINS.map(c => (
          <button key={c} onClick={() => toggle(c, selectedChains, setSelectedChains)} className={`p-3 rounded-xl border ${selectedChains.includes(c) ? "border-emerald-500 bg-emerald-500/20 text-emerald-400" : "border-gray-700 text-gray-300"}`}>{c}</button>
        ))}
      </div>
      <button onClick={() => setStep(3)} className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg w-full">Next</button>
    </div>,
    <div key="3">
      <h2 className="text-xl font-bold text-white mb-4">What are you interested in?</h2>
      <div className="flex flex-wrap gap-2 mb-4">
        {INTERESTS.map(i => (
          <button key={i} onClick={() => toggle(i, selectedInterests, setSelectedInterests)} className={`px-4 py-2 rounded-full border ${selectedInterests.includes(i) ? "border-emerald-500 bg-emerald-500/20 text-emerald-400" : "border-gray-700 text-gray-300"}`}>{i}</button>
        ))}
      </div>
      <button onClick={submit} className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg w-full">Finish</button>
    </div>,
  ];

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-2xl p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-1">
            {steps.map((_, i) => <div key={i} className={`h-1.5 w-8 rounded ${i <= step ? "bg-emerald-500" : "bg-gray-700"}`} />)}
          </div>
          <span className="text-gray-500 text-sm">{step + 1}/{steps.length}</span>
        </div>
        {steps[step]}
      </div>
    </div>
  );
}
