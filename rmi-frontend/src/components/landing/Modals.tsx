import { X, Gift, Megaphone, Award, Shield, CheckCircle2 } from 'lucide-react';

interface ModalsProps {
  showAirdropModal: boolean;
  setShowAirdropModal: (v: boolean) => void;
  showSnitchModal: boolean;
  setShowSnitchModal: (v: boolean) => void;
  showReimbursementModal: boolean;
  setShowReimbursementModal: (v: boolean) => void;
  airdropForm: { email: string; wallet: string; twitter: string };
  setAirdropForm: React.Dispatch<React.SetStateAction<{ email: string; wallet: string; twitter: string }>>;
  tipForm: { title: string; description: string; evidence: string };
  setTipForm: React.Dispatch<React.SetStateAction<{ title: string; description: string; evidence: string }>>;
}

export default function Modals({
  showAirdropModal,
  setShowAirdropModal,
  showSnitchModal,
  setShowSnitchModal,
  showReimbursementModal,
  setShowReimbursementModal,
  airdropForm,
  setAirdropForm,
  tipForm,
  setTipForm,
}: ModalsProps) {
  return (
    <>
      {/* Airdrop Waitlist Modal */}
      {showAirdropModal && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#12121a] border border-purple-500/30 rounded-2xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setShowAirdropModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-yellow-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Gift className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-2">Join V2 Airdrop Waitlist</h3>
              <p className="text-gray-400 text-sm">
                Be the first to know when $CRM V2 launches. Early adopters get bonus rewards.
              </p>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Email</label>
                <input
                  type="email"
                  placeholder="your@email.com"
                  className="w-full bg-black/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  value={airdropForm.email}
                  onChange={(e) => setAirdropForm({ ...airdropForm, email: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Wallet Address (for airdrop)</label>
                <input
                  type="text"
                  placeholder="0x..."
                  className="w-full bg-black/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  value={airdropForm.wallet}
                  onChange={(e) => setAirdropForm({ ...airdropForm, wallet: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Twitter (optional, for bonus)</label>
                <input
                  type="text"
                  placeholder="@username"
                  className="w-full bg-black/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  value={airdropForm.twitter}
                  onChange={(e) => setAirdropForm({ ...airdropForm, twitter: e.target.value })}
                />
              </div>

              <div className="p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                <p className="text-xs text-purple-400">
                  $CRM V1 holders receive 50% bonus airdrop + priority platform access.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setShowAirdropModal(false);
                  alert("Thanks for joining the V2 waitlist! We'll notify you when the airdrop goes live.");
                }}
                className="w-full py-4 bg-gradient-to-r from-purple-600 to-yellow-500 hover:from-purple-500 hover:to-yellow-400 text-white font-bold rounded-xl transition-all"
              >
                Join Waitlist
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Snitch Board Modal */}
      {showSnitchModal && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#12121a] border border-yellow-500/30 rounded-2xl max-w-lg w-full p-6 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setShowSnitchModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-2xl flex items-center justify-center mb-4">
                <Megaphone className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-2">Submit Anonymous Tip</h3>
              <p className="text-gray-400 text-sm">
                Help protect the community. Verified tips earn ETH rewards. Your identity stays anonymous.
              </p>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Tip Title</label>
                <input
                  type="text"
                  placeholder="e.g., Dev team behind multiple rugs identified"
                  className="w-full bg-black/50 border border-yellow-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-yellow-500"
                  value={tipForm.title}
                  onChange={(e) => setTipForm({ ...tipForm, title: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <textarea
                  placeholder="Describe the scam, suspicious activity, or fraud you've discovered..."
                  rows={4}
                  className="w-full bg-black/50 border border-yellow-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-yellow-500"
                  value={tipForm.description}
                  onChange={(e) => setTipForm({ ...tipForm, description: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Evidence (links, addresses, screenshots)</label>
                <textarea
                  placeholder="Contract addresses, transaction hashes, social links..."
                  rows={3}
                  className="w-full bg-black/50 border border-yellow-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-yellow-500"
                  value={tipForm.evidence}
                  onChange={(e) => setTipForm({ ...tipForm, evidence: e.target.value })}
                />
              </div>

              <div className="p-3 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                <p className="text-xs text-yellow-400">
                  <strong>Reward Tiers:</strong> Critical (1 ETH) • High (0.5 ETH) • Verified (0.1 ETH)
                </p>
              </div>

              <div className="flex items-start gap-2">
                <Shield className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-gray-500">
                  Tips are encrypted and anonymized. We never store your IP or identity.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setShowSnitchModal(false);
                  alert("Tip submitted! Our team will review and verify. You'll be notified if a reward is issued.");
                }}
                className="w-full py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-400 hover:to-yellow-500 text-black font-bold rounded-xl transition-all"
              >
                Submit Anonymous Tip
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Reimbursement Modal */}
      {showReimbursementModal && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#12121a] border border-green-500/30 rounded-2xl max-w-lg w-full p-6 relative">
            <button
              onClick={() => setShowReimbursementModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-2">1-1 Reimbursement Program</h3>
              <p className="text-gray-400 text-sm">
                Pre-register for the V2 recovery program. We help rug pull victims recover funds.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="p-3 bg-black/30 rounded-lg text-center">
                <div className="text-xl font-bold text-green-400">$547K+</div>
                <div className="text-xs text-gray-500">Recovered</div>
              </div>
              <div className="p-3 bg-black/30 rounded-lg text-center">
                <div className="text-xl font-bold text-green-400">247</div>
                <div className="text-xs text-gray-500">Victims Helped</div>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>Submit evidence and transaction details</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>Our forensics team traces the funds</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>Legal pressure and negotiations for recovery</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>No cure, no pay - we only win if you win</span>
              </div>
            </div>

            <button
              onClick={() => {
                setShowReimbursementModal(false);
                alert("Pre-registration recorded! We'll contact you when V2 recovery program launches.");
              }}
              className="w-full py-4 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-400 hover:to-green-500 text-black font-bold rounded-xl transition-all"
            >
              Pre-Register for V2 Recovery
            </button>
          </div>
        </div>
      )}
    </>
  );
}
