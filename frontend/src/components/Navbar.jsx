import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import Underline_Text from './Text-Underline'
import Button from './Button-ChangeColor'

function Navbar({ user, onSignInClick }) {
    const { logout } = useAuth();
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
    const [isHovering, setIsHovering] = useState(false);

    const handleMouseMove = (e) => {
        // Get mouse position relative to navbar
        const rect = e.currentTarget.getBoundingClientRect();
        setMousePos({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        });
    };

    return (
        <nav 
            className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-slate-500/10 border-b border-yellow-400/30 overflow-hidden hover:bg-sky-950/30"
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => setIsHovering(false)}
        >
            {/* Spotlight effect that follows mouse */}
            {isHovering && (
                <div
                    className="absolute pointer-events-none transition-opacity duration-300"
                    style={{
                        left: `${mousePos.x}px`,
                        top: `${mousePos.y}px`,
                        transform: 'translate(-50%, -50%)',
                        width: '300px',
                        height: '300px',
                        background: 'radial-gradient(circle, rgba(255, 214, 0, 0.15) 0%, transparent 70%)',
                        opacity: isHovering ? 1 : 0,
                    }}
                />
            )}

            <div className="container mx-auto px-6 py-4 relative z-10">
                <div className="flex items-center justify-between">

                    {/* Left: Logo */}
                    <div className="text-4xl font-bold text-yellow-400">
                        LottoAI
                    </div>

                    {/* Center: Navigation Links 
                    These are the HTML anchor jumps behavior - no custom eventhandler 
                    -> href is important here and section id in App.jsx */}
                    <div className="hidden md:flex gap-20">

                        <Underline_Text href="#intro">INTRO</Underline_Text>

                        <Underline_Text href="#process">HOW IT WORKS</Underline_Text>

                        <Underline_Text href="#subscribe">SUBSCRIBE</Underline_Text>            

                    </div>

                    {/* Right: Auth Section */}
                    <div className="hidden md:flex gap-3 items-center">
                        {user ? (
                            // Logged in: show username and logout
                            <>
                                <span className="text-yellow-400 mr-2">
                                    Welcome, {user.username}
                                </span>
                                <Button onClick={logout}>LOG OUT</Button>
                            </>
                        ) : (
                            // Not logged in: show sign in button
                            <Button onClick={onSignInClick}>SIGN IN</Button>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;