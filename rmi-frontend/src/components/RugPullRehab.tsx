/**
 * Rug Pull Rehab - Educational classes booking system
 */
import { useState } from 'react';
import { 
  GraduationCap, 
  Calendar, 
  Clock, 
  Users,
  Check,
  Star,
  Video,
  FileText,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  ArrowRight
} from 'lucide-react';
import { useAppStore } from '../store/appStore';

const CLASS_DURATION = 2; // hours
const CLASS_PRICE = 100; // USD

const TIME_SLOTS = [
  { time: '10:00', available: true },
  { time: '14:00', available: true },
  { time: '18:00', available: false },
];

const WEEKEND_SLOTS = [
  { time: '12:00', available: true },
  { time: '16:00', available: true },
];

const UPCOMING_CLASSES = [
  {
    id: 1,
    title: 'Honeypot Detection 101',
    description: 'Learn to spot hidden mint functions, blacklists, and sell restrictions before you buy.',
    instructor: 'RugHunter_007',
    instructorRep: 2456,
    date: '2024-01-20',
    time: '14:00',
    timezone: 'UTC',
    spots: 8,
    totalSpots: 20,
    tier: 'BASIC+',
    image: 'honeypot'
  },
  {
    id: 2,
    title: 'Reading Smart Contracts',
    description: 'Understand what you\'re actually agreeing to when you approve a contract.',
    instructor: 'DeFi_Detective',
    instructorRep: 1892,
    date: '2024-01-22',
    time: '10:00',
    timezone: 'UTC',
    spots: 12,
    totalSpots: 20,
    tier: 'PRO+',
    image: 'contract'
  },
  {
    id: 3,
    title: 'Whale Tracking Mastery',
    description: 'Follow smart money movements and understand accumulation vs distribution patterns.',
    instructor: 'WhaleWatcher',
    instructorRep: 892,
    date: '2024-01-25',
    time: '16:00',
    timezone: 'UTC',
    spots: 5,
    totalSpots: 15,
    tier: 'ELITE',
    image: 'whale'
  },
];

const TESTIMONIALS = [
  {
    quote: "This class saved me from 3 subsequent rugs. I can now read contracts in 30 seconds.",
    author: "@SavedByEducation",
    class: "Reading Smart Contracts"
  },
  {
    quote: "The honeypot detection techniques alone were worth 10x the price. Life-changing.",
    author: "@RugSurvivor",
    class: "Honeypot Detection 101"
  },
  {
    quote: "Finally understood how to actually track whales instead of just guessing.",
    author: "@AlphaHunter",
    class: "Whale Tracking Mastery"
  }
];

const INCLUDES = [
  '2-hour live Zoom session',
  'Recording available for 7 days',
  'Class notes and resources',
  'Q&A with instructor',
  'Certificate of completion',
  '1-week Telegram support',
];

export default function RugPullRehab() {
  const [view, setView] = useState<'list' | 'booking' | 'confirmation'>('list');
  const [selectedClass, setSelectedClass] = useState<typeof UPCOMING_CLASSES[0] | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'eth' | 'usdc' | 'usdt' | 'card'>('eth');

  const user = useAppStore((state) => state.user);
  const tier = user?.tier || 'FREE';
  
  // Check if user gets free classes
  const freeClassesRemaining = tier === 'ELITE' ? 1 : tier === 'ENTERPRISE' ? 'Unlimited' : 0;
  const discount = tier === 'PRO' ? 0.2 : tier === 'BASIC' ? 0 : 0;
  const finalPrice = CLASS_PRICE * (1 - discount);

  const handleBook = (cls: typeof UPCOMING_CLASSES[0]) => {
    setSelectedClass(cls);
    setView('booking');
  };

  const handleConfirm = () => {
    setView('confirmation');
  };

  // Generate calendar days
  const generateCalendar = () => {
    const days = [];
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const calendarDays = generateCalendar();

  if (view === 'confirmation' && selectedClass) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-green-400" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-4">You're Booked!</h2>
        <p className="text-gray-400 mb-8">
          Your spot is reserved for <span className="text-white font-semibold">{selectedClass.title}</span> on{' '}
          {selectedClass.date} at {selectedTime}.
        </p>
        
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6 mb-8 text-left">
          <h3 className="font-semibold text-white mb-4">What happens next?</h3>
          <ol className="space-y-3 text-gray-400 text-left">
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">1</span>
              Check your email for the Zoom link (sent immediately)
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">2</span>
              Join the Telegram group for class materials
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">3</span>
              Show up 5 minutes early to say hi
            </li>
            <li className="flex items-start gap-3">
              <span className="w-6 h-6 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">4</span>
              Recording will be available for 7 days if you miss it
            </li>
          </ol>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            onClick={() => setView('list')}
            className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium"
          >
            Book Another Class
          </button>
          <a 
            href="/dashboard"
            className="px-6 py-3 bg-green-500 hover:bg-green-600 text-black font-bold rounded-lg"
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    );
  }

  if (view === 'booking' && selectedClass) {
    return (
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <button 
          onClick={() => setView('list')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-6"
        >
          <ChevronLeft className="w-5 h-5" />
          Back to Classes
        </button>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Class Info */}
          <div>
            <div className="aspect-video bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded-xl flex items-center justify-center mb-4">
              <GraduationCap className="w-16 h-16 text-orange-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">{selectedClass.title}</h2>
            <p className="text-gray-400 mb-4">{selectedClass.description}</p>
            
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
                {selectedClass.instructor.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <div className="font-medium text-white">{selectedClass.instructor}</div>
                <div className="text-sm text-gray-500">Rep: {selectedClass.instructorRep}</div>
              </div>
            </div>

            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <Video className="w-4 h-4" />
                Live Zoom Session
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {CLASS_DURATION} hours
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4" />
                {selectedClass.spots} of {selectedClass.totalSpots} spots remaining
              </div>
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Recording available 7 days
              </div>
            </div>
          </div>

          {/* Booking Form */}
          <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
            <h3 className="font-semibold text-white mb-4">Select Date & Time</h3>
            
            {/* Calendar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <button 
                  onClick={() => {
                    const prev = new Date(selectedDate);
                    prev.setMonth(prev.getMonth() - 1);
                    setSelectedDate(prev);
                  }}
                  className="p-1 hover:bg-gray-800 rounded"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="font-medium">
                  {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </span>
                <button 
                  onClick={() => {
                    const next = new Date(selectedDate);
                    next.setMonth(next.getMonth() + 1);
                    setSelectedDate(next);
                  }}
                  className="p-1 hover:bg-gray-800 rounded"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
              <div className="grid grid-cols-7 gap-1 text-center text-sm">
                {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(d => (
                  <div key={d} className="text-gray-500 py-2">{d}</div>
                ))}
                {calendarDays.slice(0, 35).map((date, idx) => {
                  const isSelected = date.toDateString() === selectedDate.toDateString();
                  const isPast = date < new Date();
                  return (
                    <button
                      key={idx}
                      onClick={() => !isPast && setSelectedDate(date)}
                      disabled={isPast}
                      className={`py-2 rounded-lg text-sm ${
                        isSelected 
                          ? 'bg-orange-500 text-white' 
                          : isPast 
                            ? 'text-gray-600 cursor-not-allowed'
                            : 'hover:bg-gray-800 text-gray-300'
                      }`}
                    >
                      {date.getDate()}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Time Slots */}
            <div className="mb-6">
              <h4 className="text-sm text-gray-400 mb-3">Available Times</h4>
              <div className="grid grid-cols-3 gap-2">
                {(selectedDate.getDay() === 0 || selectedDate.getDay() === 6 ? WEEKEND_SLOTS : TIME_SLOTS).map((slot) => (
                  <button
                    key={slot.time}
                    onClick={() => slot.available && setSelectedTime(slot.time)}
                    disabled={!slot.available}
                    className={`py-2 px-3 rounded-lg text-sm font-medium ${
                      selectedTime === slot.time
                        ? 'bg-orange-500 text-white'
                        : slot.available
                          ? 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                          : 'bg-gray-900 text-gray-600 cursor-not-allowed'
                    }`}
                  >
                    {slot.time}
                  </button>
                ))}
              </div>
            </div>

            {/* Payment */}
            <div className="mb-6">
              <h4 className="text-sm text-gray-400 mb-3">Payment Method</h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'eth', label: 'ETH', icon: '⧫' },
                  { id: 'usdc', label: 'USDC', icon: '$' },
                  { id: 'usdt', label: 'USDT', icon: '₮' },
                  { id: 'card', label: 'Card', icon: '💳' },
                ].map((method) => (
                  <button
                    key={method.id}
                    onClick={() => setPaymentMethod(method.id as any)}
                    className={`py-2 px-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2 ${
                      paymentMethod === method.id
                        ? 'bg-green-500 text-black'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    <span>{method.icon}</span>
                    {method.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Price Summary */}
            <div className="border-t border-gray-800 pt-4 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">Class Price</span>
                <span className="text-white">${CLASS_PRICE}</span>
              </div>
              {discount > 0 && (
                <div className="flex justify-between items-center mb-2 text-green-400">
                  <span>{tier} Discount ({discount * 100}%)</span>
                  <span>-${(CLASS_PRICE * discount).toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between items-center text-lg font-bold">
                <span className="text-white">Total</span>
                <span className="text-green-400">
                  {freeClassesRemaining ? 'FREE' : `$${finalPrice.toFixed(2)}`}
                </span>
              </div>
            </div>

            {/* Book Button */}
            <button
              onClick={handleConfirm}
              disabled={!selectedTime}
              className="w-full py-3 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-700 disabled:text-gray-500 text-black font-bold rounded-lg transition-colors"
            >
              {freeClassesRemaining ? 'Confirm Free Booking' : `Pay $${finalPrice.toFixed(2)}`}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-500/10 border border-orange-500/30 rounded-full mb-4">
          <GraduationCap className="w-5 h-5 text-orange-400" />
          <span className="text-orange-400 font-medium">Learn. Heal. Prevent.</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4">
          Rug Pull <span className="text-orange-400">Rehab</span>
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          $100/2-hour classes with industry experts. Learn how scams work, spot warning signs, 
          and never get rugged again. ELITE members get 1 free class per month.
        </p>
      </div>

      {/* User Benefits */}
      {tier !== 'FREE' && (
        <div className="bg-gradient-to-r from-orange-500/10 to-yellow-500/10 border border-orange-500/20 rounded-xl p-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-500/20 rounded-full flex items-center justify-center">
                <Star className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">{tier} Member Benefits</h3>
                <p className="text-gray-400 text-sm">
                  {freeClassesRemaining === 'Unlimited' ? (
                    'Unlimited free classes included'
                  ) : freeClassesRemaining > 0 ? (
                    `${freeClassesRemaining} free class remaining this month`
                  ) : discount > 0 ? (
                    `${discount * 100}% discount on all classes`
                  ) : (
                    'Book classes at full price'
                  )}
                </p>
              </div>
            </div>
            {freeClassesRemaining && (
              <span className="px-4 py-2 bg-green-500/20 text-green-400 rounded-full font-medium">
                {freeClassesRemaining === 'Unlimited' ? 'All Classes FREE' : `${freeClassesRemaining} Free Class Left`}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Upcoming Classes */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Upcoming Classes</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {UPCOMING_CLASSES.map((cls) => (
            <div key={cls.id} className="bg-[#12121a] border border-gray-800 rounded-xl overflow-hidden hover:border-orange-500/30 transition-colors">
              <div className="aspect-video bg-gradient-to-br from-orange-500/20 to-red-500/20 flex items-center justify-center">
                <GraduationCap className="w-12 h-12 text-orange-400" />
              </div>
              <div className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-orange-500/20 text-orange-400 text-xs rounded-full">
                    {cls.tier}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    cls.spots < 5 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                  }`}>
                    {cls.spots} spots left
                  </span>
                </div>
                <h3 className="font-semibold text-white mb-2">{cls.title}</h3>
                <p className="text-gray-400 text-sm mb-4">{cls.description}</p>
                
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center text-xs font-bold">
                    {cls.instructor.slice(0, 2).toUpperCase()}
                  </div>
                  <div className="text-sm">
                    <div className="text-gray-300">{cls.instructor}</div>
                    <div className="text-gray-500">Rep: {cls.instructorRep}</div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-400 mb-4">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {cls.date}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {cls.time} {cls.timezone}
                  </div>
                </div>

                <button
                  onClick={() => handleBook(cls)}
                  className="w-full py-2 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  Book Now
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* What's Included */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">What's Included</h3>
          <ul className="space-y-3">
            {INCLUDES.map((item, idx) => (
              <li key={idx} className="flex items-center gap-3">
                <Check className="w-5 h-5 text-green-400" />
                <span className="text-gray-300">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Student Testimonials</h3>
          <div className="space-y-4">
            {TESTIMONIALS.map((t, idx) => (
              <div key={idx} className="p-4 bg-gray-800/50 rounded-lg">
                <p className="text-gray-300 text-sm mb-2">"{t.quote}"</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">{t.author}</span>
                  <span className="text-orange-400">{t.class}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* FAQ */}
      <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">Frequently Asked Questions</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            {
              q: "What if I miss the live class?",
              a: "All classes are recorded and available for 7 days. You'll get the recording link via email."
            },
            {
              q: "Can I get a refund?",
              a: "Full refund if you cancel 24 hours before the class. No refunds for no-shows."
            },
            {
              q: "Do I need any prior knowledge?",
              a: "Classes are designed for all levels. We start with basics and build up."
            },
            {
              q: "What payment methods are accepted?",
              a: "ETH, USDC, USDT, and credit cards. Crypto payments get a 5% discount."
            },
          ].map((faq, idx) => (
            <div key={idx}>
              <h4 className="font-medium text-white mb-1">{faq.q}</h4>
              <p className="text-gray-400 text-sm">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
