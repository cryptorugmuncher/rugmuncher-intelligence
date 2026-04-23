import { Shield, AlertTriangle, Lock } from 'lucide-react';

interface FooterProps {
  onNavigate: (page: string) => void;
  onScrollToSection: (id: string) => void;
}

export default function Footer({ onNavigate, onScrollToSection }: FooterProps) {
  return (
    <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-purple-500/20">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-yellow-400 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-gradient">Rug Munch</span>
            </div>
            <p className="text-gray-500 text-sm">
              AI-powered Web3 security. Don't get rugged. V2 is live.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-purple-400">Telegram Bots</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="https://t.me/rugmunchbot" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">@rugmunchbot</a></li>
              <li><a href="https://t.me/rmi_alerts_bot" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">@rmi_alerts_bot</a></li>
              <li><a href="https://t.me/rmi_alpha_bot" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">@rmi_alpha_bot</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-purple-400">Platform</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><button onClick={() => onNavigate('scanner')} className="hover:text-white transition-colors text-left">Token Scanner</button></li>
              <li><button onClick={() => onNavigate('clustering')} className="hover:text-white transition-colors text-left">Muncher Maps</button></li>
              <li><button onClick={() => onNavigate('trenches')} className="hover:text-white transition-colors text-left">The Trenches</button></li>
              <li><button onClick={() => onNavigate('rehab')} className="hover:text-white transition-colors text-left">Rug Pull Rehab</button></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-purple-400">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><button onClick={() => onScrollToSection('faq')} className="hover:text-white transition-colors text-left">FAQ</button></li>
              <li><button onClick={() => onScrollToSection('v2-waitlist')} className="hover:text-white transition-colors text-left">Token Utility</button></li>
              <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              <li><a href="https://twitter.com/CryptoRugMunch" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">X / Twitter</a></li>
            </ul>
          </div>
        </div>

        {/* Legal Bar */}
        <div className="mt-8 p-6 bg-slate-900/50 border border-slate-800 rounded-xl">
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-yellow-500 text-sm mb-1">Risk Disclosure & Legal Notice</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Cryptocurrency trading involves substantial risk of loss. Rug Munch Intelligence provides automated risk analysis tools only — not investment advice, not financial advice, and not trading recommendations. Past performance of our detection algorithms does not guarantee future results. Always conduct your own due diligence before investing. Never invest more than you can afford to lose entirely. The content on this platform is for informational and educational purposes only.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 mb-4">
            <Shield className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-purple-400 text-sm mb-1">No Warranty & Limitation of Liability</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                Rug Munch Media LLC and its affiliates provide all services, scans, reports, and intelligence "as is" without any warranty of any kind, express or implied. We do not guarantee the accuracy, completeness, or timeliness of any scan result, alert, or analysis. Under no circumstances shall Rug Munch Media LLC be liable for any direct, indirect, incidental, special, or consequential damages arising from the use of or inability to use our platform, even if advised of the possibility of such damages. By using this platform, you agree to hold harmless and indemnify Rug Munch Media LLC from any claims, losses, or damages.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Lock className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-400 text-sm mb-1">Jurisdiction & Governing Law</h4>
              <p className="text-xs text-gray-500 leading-relaxed">
                These terms and your use of the Rug Munch platform shall be governed by and construed in accordance with the laws of the State of Wyoming, United States, without regard to conflict of law principles. Rug Munch Media LLC is a Wyoming limited liability company. Any dispute arising from these terms or your use of the platform shall be resolved exclusively in the state or federal courts located in Wyoming. By accessing this platform, you consent to the personal jurisdiction of such courts.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-gray-800 text-center">
          <p className="text-sm text-gray-400 font-semibold">
            © 2026 Rug Munch Media LLC. All Rights Reserved.
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Rug Munch Media LLC • Wyoming Limited Liability Company • t.me/rugmunchbot • x.com/CryptoRugMunch
          </p>
          <p className="text-[10px] text-gray-700 mt-3 max-w-2xl mx-auto">
            $CRM token reimbursement subject to verification of wallet ownership and exclusion of addresses involved in the March 2026 syndicate infiltration. 1-to-1 reimbursement applies only to holders uninvolved with the coordinated extraction event, as determined by on-chain forensic analysis. Snapshot date and distribution mechanics will be announced via official X @CryptoRugMunch and Telegram @rugmunchbot channels only. Beware of impersonators.
          </p>
        </div>
      </div>
    </footer>
  );
}
