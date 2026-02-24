import { useEffect, useState, useRef } from 'react';
import { useAnimation } from 'framer-motion';
import { useAuth } from './hooks/useAuth';
import "./index.css";
import Navbar from "./components/Navbar";
import LightRays from "./components/LightRays";
import ProcessBox from './components/ProcessBox';
import AnimatedArrow from './components/AnimatedArrow';
import CenterCard from './components/CenterCard';
import Form from './components/Form-UploadImage';
import SignInForm from './components/Form-SignIn';
import SignUpForm from './components/Form-SignUp';

function App() {
  const { user } = useAuth();

  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const error = params.get('error');

    if (token) {
      // Store token and reload
      localStorage.setItem('access_token', token);
      window.location.href = '/'; // Refresh to load user
    } else if (error) {
      alert('Google sign-in failed. Please try again.');
      window.location.href = '/'; // Clean URL
    }
  }, []);

  const [showBoxes, setShowBoxes] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [authMode, setAuthMode] = useState('signin') // 'signin' or 'signup'

  // Animation controls for each element
  const ticketControls = useAnimation();
  const arrowRightControls = useAnimation();
  const extractControls = useAnimation();
  const arrowDownControls = useAnimation();
  const compareControls = useAnimation();
  const arrowLeftControls = useAnimation();
  const winControls = useAnimation();
  const arrowUpControls = useAnimation();

  // Track if animation is running
  const isAnimatingRef = useRef(false);

  useEffect(() => {
    let ticking = false;
    
    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrollPos = window.scrollY;
          const windowHeight = window.innerHeight;
          
          // Calculate scroll percentage (0 to 1)
          const scrollPct = Math.min(scrollPos / windowHeight, 1);
          
          // Update CSS custom properties for animations
          document.documentElement.style.setProperty('--scroll-pct', scrollPct);
          document.documentElement.style.setProperty('--hero-scale', 1 - scrollPct * 0.2); // Scale from 1.0 to 0.8
          document.documentElement.style.setProperty('--hero-opacity', 1 - scrollPct * 0.8); // Fade out
          document.documentElement.style.setProperty('--hero-translateY', `${-scrollPct * 60}vh`); // Move up
          document.documentElement.style.setProperty('--process-opacity', scrollPct * 1.5); // Fade in process
          
          // Trigger process boxes animation when section comes into view
          if (scrollPos > windowHeight * 0.7 && !showBoxes) {
            setShowBoxes(true);
          }

          // Subscribe section fade-in (starts when user reaches ~2 viewport heights)
          const subscribeSection = document.querySelector('.subscribe-section');
          if (subscribeSection) {
            const subscribeSectionTop = subscribeSection.offsetTop;
            const distanceFromTop = subscribeSectionTop - scrollPos - windowHeight;
            const fadeInStart = windowHeight * 0.3; // Start fading in when 30% from view
            
            if (distanceFromTop < fadeInStart) {
              const fadeProgress = Math.min(1, 1 - (distanceFromTop / fadeInStart));
              document.documentElement.style.setProperty('--subscribe-opacity', fadeProgress);
              document.documentElement.style.setProperty('--subscribe-translateY', `${(1 - fadeProgress) * 40}px`);
            } else {
              document.documentElement.style.setProperty('--subscribe-opacity', 0);
              document.documentElement.style.setProperty('--subscribe-translateY', '40px');
            }
          }

          // Toggle scroll indicator
          const scrollIndicator = document.querySelector('.scroll-down');
          if (scrollIndicator) {
            if (scrollPos > 100) {
              scrollIndicator.classList.add('removed');
            } else {
              scrollIndicator.classList.remove('removed');
            }
          }

          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [showBoxes]);

  // Orchestrate the circuit animation sequence
  useEffect(() => {
    if (!showBoxes) return;
    
    // Prevent multiple instances
    if (isAnimatingRef.current) return;

    const runCircuitAnimation = async () => {
      isAnimatingRef.current = true;

      // CRITICAL: Wait for components to mount before animating
      await new Promise(resolve => setTimeout(resolve, 100));

      // Infinite loop
      while (true) {
        try {
          // Step 1: Ticket → Extract
          await ticketControls.start({ opacity: 1, scale: 1, transition: { duration: 0.6 } });
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          // Draw line (extend)
          await arrowRightControls.start({ pathLength: 1, opacity: 1, transition: { duration: 0.8 } });
          await new Promise(resolve => setTimeout(resolve, 400));
          
          // Next box fades in
          extractControls.start({ opacity: 1, scale: 1, transition: { duration: 0.6 } });
          await ticketControls.start({ opacity: 0, scale: 0.8, transition: { duration: 0.6 } });
          
          // Line fades out (keep pathLength at 1, only fade opacity)
          await arrowRightControls.start({ opacity: 0, transition: { duration: 0.4 } });
          // Reset pathLength to 0 invisibly for next animation
          arrowRightControls.set({ pathLength: 0 });
          
          // Step 2: Extract → Compare
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          await arrowDownControls.start({ pathLength: 1, opacity: 1, transition: { duration: 0.8 } });
          await new Promise(resolve => setTimeout(resolve, 400));
          
          compareControls.start({ opacity: 1, scale: 1, transition: { duration: 0.6 } });
          await extractControls.start({ opacity: 0, scale: 0.8, transition: { duration: 0.6 } });
          
          await arrowDownControls.start({ opacity: 0, transition: { duration: 0.4 } });
          arrowDownControls.set({ pathLength: 0 });
          
          // Step 3: Compare → Win
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          await arrowLeftControls.start({ pathLength: 1, opacity: 1, transition: { duration: 0.8 } });
          await new Promise(resolve => setTimeout(resolve, 400));
          
          winControls.start({ opacity: 1, scale: 1, transition: { duration: 0.6 } });
          await compareControls.start({ opacity: 0, scale: 0.8, transition: { duration: 0.6 } });
          
          await arrowLeftControls.start({ opacity: 0, transition: { duration: 0.4 } });
          arrowLeftControls.set({ pathLength: 0 });
          
          // Step 4: Win → Ticket (complete circuit)
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          await arrowUpControls.start({ pathLength: 1, opacity: 1, transition: { duration: 0.8 } });
          await new Promise(resolve => setTimeout(resolve, 400));
          
          ticketControls.start({ opacity: 1, scale: 1, transition: { duration: 0.6 } });
          await winControls.start({ opacity: 0, scale: 0.8, transition: { duration: 0.6 } });
          
          await arrowUpControls.start({ opacity: 0, transition: { duration: 0.4 } });
          arrowUpControls.set({ pathLength: 0 });
          
          // Brief pause before restarting loop
          await new Promise(resolve => setTimeout(resolve, 500));
          
        } catch (error) {
          console.error('❌ Animation error:', error);
          break;
        }
      }
    };

    runCircuitAnimation();
    
    // Cleanup on unmount
    return () => {
      isAnimatingRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showBoxes]);

  return (
    <div className="relative">

      {/* Navbar */}
      <Navbar
        user={user} 
        onSignInClick={() => {
          setAuthMode('signin');
          setIsAuthModalOpen(true);
        }} 
      />

      {/* Hero Section - Shrinks and fades on scroll */}
      <section
        id="intro"
        className="hero-section relative min-h-screen bg-cover bg-center bg-fixed flex items-center justify-center scroll-mt-0"
        style={{
          backgroundImage: "url('/background_image/blue_and_gold_marble.jpg')"
        }}
      >
        {/* Light Rays */}
        <LightRays />

        {/* Radial gradient overlay for text contrast */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,0,0,0.6)_0%,rgba(0,0,0,0.3)_40%,transparent_70%)]" />

        {/* Hero Content - Animates on scroll */}
        <div className="hero-content relative z-10 text-center px-4 space-y-6">

          <h1 className="text-6xl md:text-8xl font-bold text-yellow-400 drop-shadow-[0_0_40px_rgba(0,0,0,1)]">
            Test Your Fortune
          </h1>

          <p className="text-xl md:text-2xl text-gray-100 max-w-2xl mx-auto drop-shadow-[0_2px_10px_rgba(0,0,0,0.8)]">
            Not just another lottery app. Our built-in AI system will help you secure your prize just through your ticket image.
          </p>
        </div>

        {/* Scroll Down Indicator */}
        <div className="scroll-down font-bold">
          Scroll Down
        </div>

      </section>

      {/* Process Section - Circuit Layout */}
      <section 
        id="process"
        className="process-section relative bg-gradient-to-b from-black via-gray-900 to-black flex items-center justify-center pt-10 pb-8"
      >
        <div className="relative max-w-4xl mx-auto px-1">
          
          {/* Grid Layout - very compact */}
          <div className="grid grid-cols-3 grid-rows-3 gap-x-1 gap-y-2 items-center">
            
            {/* Top Left: Ticket */}
            <div className="col-start-1 row-start-1 flex justify-center">
              {showBoxes && <ProcessBox icon="🎫" label="Ticket" controls={ticketControls} />}
            </div>
            
            {/* Top Center: Arrow Right */}
            <div className="col-start-2 row-start-1 flex justify-center">
              {showBoxes && <AnimatedArrow direction="right" controls={arrowRightControls} />}
            </div>
            
            {/* Top Right: Extract */}
            <div className="col-start-3 row-start-1 flex justify-center">
              {showBoxes && <ProcessBox icon="🔍" label="Extract" controls={extractControls} />}
            </div>
            
            {/* Middle Right: Arrow Down */}
            <div className="col-start-3 row-start-2 flex justify-center">
              {showBoxes && <AnimatedArrow direction="down" controls={arrowDownControls} />}
            </div>
            
            {/* Center: Main Card */}
            <div className="col-start-2 row-start-2 flex justify-center">
              <CenterCard onTryNowClick={() => setIsModalOpen(true)} />
            </div>
            
            {/* Bottom Right: Compare */}
            <div className="col-start-3 row-start-3 flex justify-center">
              {showBoxes && <ProcessBox icon="📊" label="Compare" controls={compareControls} />}
            </div>
            
            {/* Bottom Center: Arrow Left */}
            <div className="col-start-2 row-start-3 flex justify-center">
              {showBoxes && <AnimatedArrow direction="left" controls={arrowLeftControls} />}
            </div>
            
            {/* Bottom Left: Win */}
            <div className="col-start-1 row-start-3 flex justify-center">
              {showBoxes && <ProcessBox icon="🎉" label="Win!!!" controls={winControls} />}
            </div>
            
            {/* Middle Left: Arrow Up (completes the circuit) */}
            <div className="col-start-1 row-start-2 flex justify-center">
              {showBoxes && <AnimatedArrow direction="up" controls={arrowUpControls} />}
            </div>
          </div>
        </div>
      </section>

      {/* Subscribe Section */}
      <section
        id="subscribe" 
        className="subscribe-section relative min-h-screen flex items-center justify-center py-20"
        style={{
          backgroundImage: "url('/background_image/gold_and_navy_marble.jpg')"
        }}
      >
        {/* Light overlay for contrast */}
        <div className="absolute inset-0 bg-black/50" />
        
        <div className="relative z-10 text-center max-w-3xl px-4 w-full">
          {/* Title with shadow */}
          <h2 className="text-5xl md:text-6xl font-bold text-yellow-400 mb-6 drop-shadow-[0_0_30px_rgba(0,0,0,1)]">
            Never Miss a Draw
          </h2>
          <p className="text-gray-200 text-lg md:text-xl mb-10 drop-shadow-[0_0_20px_rgba(0,0,0,0.8)]">
            Subscribe for instant notifications on winning numbers
          </p>
          
          {/* Glass container for input/button */}
          <div className="bg-black/70 backdrop-blur-xl border-2 border-yellow-400/40 rounded-2xl p-8 md:p-10 shadow-[0_0_50px_rgba(255,215,0,0.3)] max-w-2xl mx-auto">
            <form className="flex flex-col sm:flex-row gap-4">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 bg-black/50 border-2 border-yellow-400/30 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 transition-all"
                required
              />
              <button
                type="submit"
                className="px-8 py-4 bg-yellow-400 hover:bg-yellow-500 text-black font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:scale-105 whitespace-nowrap"
              >
                Subscribe →
              </button>
            </form>
            <p className="text-gray-400 text-sm mt-4">
              Join 10,000+ subscribers. No spam, unsubscribe anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Modal for Upload Form */}
      {isModalOpen && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setIsModalOpen(false)}
        >
          <div 
            className="relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute -top-10 right-0 text-white hover:text-yellow-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
            <Form />
          </div>
        </div>
      )}

      {/* Auth Modal (Sign In / Sign Up) */}
      {isAuthModalOpen && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setIsAuthModalOpen(false)}
        >
          <div 
            className="relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setIsAuthModalOpen(false)}
              className="absolute -top-10 right-0 text-white hover:text-yellow-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
            
            {authMode === 'signin' ? (
              <SignInForm 
                onSwitchToSignUp={() => setAuthMode('signup')} 
                onClose={() => setIsAuthModalOpen(false)}
              />
            ) : (
              <SignUpForm 
                onSwitchToSignIn={() => setAuthMode('signin')} 
                onClose={() => setIsAuthModalOpen(false)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;