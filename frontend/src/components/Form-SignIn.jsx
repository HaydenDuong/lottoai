import { useState } from 'react';
import styled from 'styled-components';
import { useAuth } from '../hooks/useAuth';

const SignIn_Form = ({ onSwitchToSignUp, onClose }) => {
  const { login, googleLogin } = useAuth();  // Get login function from AuthContext
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);  // Call AuthContext login function
      
      // Success! Close modal
      if (onClose) onClose();
      
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <StyledWrapper>
      <form id="login-form" onSubmit={handleSubmit}>
        <div className="header-form">
          <span className="title">Welcome back!</span>
          <span className="subtitle">Sign in to continue</span>
        </div>

        {error && <div className="error-message">{error}</div>}

        <input 
          type="email" 
          id="login-email" 
          placeholder="Email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required 
          disabled={loading}
        />
        
        <input 
          type="password" 
          id="login-password" 
          placeholder="Password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required 
          disabled={loading}
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
        
        <div className="division-or">
          <div className="h-line" />
          <span>or</span>
          <div className="h-line" />
        </div>
        
        <button 
          type="button" 
          id="google-btn" 
          onClick={googleLogin}
          disabled={loading}
        >
          Continue with Google
        </button>
        
        <button 
          type="button" 
          id="signup-btn" 
          onClick={onSwitchToSignUp}
          disabled={loading}
        >
          Create an account
        </button>
      </form>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
  #login-form {
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(255, 215, 0, 0.4);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 0 50px rgba(255, 215, 0, 0.3);
    max-width: 450px;
    min-width: 350px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  #login-form .header-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;
  }

  #login-form .header-form .title {
    font-size: 36px;
    font-weight: bold;
    color: #FFD700;
    margin-bottom: 8px;
  }

  #login-form .header-form .subtitle {
    color: #E5E5E5;
    font-size: 16px;
  }

  .error-message {
    background: rgba(255, 0, 0, 0.1);
    border: 1px solid rgba(255, 0, 0, 0.3);
    border-radius: 8px;
    padding: 10px;
    color: #ff6b6b;
    font-size: 14px;
    text-align: center;
  }

  #login-form input {
    padding: 14px 18px;
    border: 2px solid rgba(255, 215, 0, 0.3);
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.5);
    color: #FFFFFF;
    font-size: 15px;
    outline: none;
    transition: all 0.3s ease;
  }

  #login-form input::placeholder {
    color: rgba(229, 229, 229, 0.5);
  }

  #login-form input:focus {
    border-color: #FFD700;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
  }

  #login-form input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  #login-form button {
    padding: 14px 20px;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    font-size: 15px;
    transition: all 0.3s ease;
    border: none;
  }

  #login-form button[type="submit"] {
    background: #FFD700;
    color: #000;
    box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
  }
  
  #login-form button[type="submit"]:hover:not(:disabled) {
    background: #FFA500;
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(255, 215, 0, 0.4);
  }

  #login-form button:disabled {
    background: rgba(255, 215, 0, 0.2);
    color: rgba(229, 229, 229, 0.3);
    cursor: not-allowed;
    transform: none;
  }

  #login-form #google-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 215, 0, 0.3);
    color: #E5E5E5;
  }
  
  #login-form #google-btn:hover:not(:disabled) {
    background: rgba(255, 215, 0, 0.15);
    border-color: #FFD700;
  }

  #login-form #signup-btn {
    background: rgba(0, 0, 0, 0.5);
    border: 2px solid rgba(255, 215, 0, 0.5);
    color: #FFD700;
  }
  
  #login-form #signup-btn:hover:not(:disabled) {
    background: rgba(255, 215, 0, 0.1);
    border-color: #FFD700;
  }

  #login-form .division-or {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 10px 0;
  }
  
  #login-form .division-or span {
    color: rgba(229, 229, 229, 0.6);
    font-size: 14px;
  }
  
  #login-form .h-line {
    flex: 1;
    height: 1px;
    background: rgba(255, 215, 0, 0.3);
  }
`;

export default SignIn_Form;