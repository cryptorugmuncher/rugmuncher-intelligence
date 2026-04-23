import { MessageCircle, Bot } from 'lucide-react';
import ScrollReveal from '../hero/ScrollReveal';

const FOUNDER_QUOTES = [
  {
    quote: "I will be implementing a 1-1 token reimbursement. Whatever the final structure looks like, the bottom line is this: you will receive the exact same number of tokens you held prior to this event occurring.",
    date: "Mar 31, 2026",
    context: "On V2 token reimbursement"
  },
  {
    quote: "Words and promises aren't going to fix this. The only thing that will make this right is absolute transparency.",
    date: "Mar 31, 2026",
    context: "On the $CRM investigation"
  },
  {
    quote: "When I ran our bot over the data, it flagged coordinated patterns that no random group of traders could ever replicate by accident. This is the ultimate proof of concept for $CRM.",
    date: "Mar 30, 2026",
    context: "On catching the syndicate"
  },
  {
    quote: "Our mission has always been to find and expose scams. That mission hasn't changed, and I am not giving up.",
    date: "Mar 29, 2026",
    context: "On taking sole control"
  }
];

export default function FoundersWordSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-purple-500/5 to-transparent">
      <div className="max-w-5xl mx-auto">
        <ScrollReveal direction="up" distance={30}>
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full mb-4">
              <MessageCircle className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">@CryptoRugMunch</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-3">
              Straight From The <span className="text-purple-400">Founder</span>
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Every promise, every update, every wallet consolidation — documented publicly on X.
            </p>
          </div>
        </ScrollReveal>

        <div className="grid md:grid-cols-2 gap-6">
          {FOUNDER_QUOTES.map((item, idx) => (
            <ScrollReveal key={idx} direction="up" distance={20} delay={idx * 100}>
              <div className="bg-[#12121a] border border-slate-800 rounded-xl p-6 hover:border-purple-500/20 transition-all">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-yellow-400 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="font-semibold text-white text-sm">@CryptoRugMunch</div>
                    <div className="text-xs text-slate-500">{item.date}</div>
                  </div>
                  <span className="ml-auto text-[10px] px-2 py-1 bg-purple-500/10 text-purple-400 rounded-full border border-purple-500/20">
                    {item.context}
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed italic">
                  "{item.quote}"
                </p>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
