import { useState } from 'react';
import styled from 'styled-components';
import { useAuth } from '../hooks/useAuth';

const SignUp_Form = ({ onSwitchToSignIn, onClose }) => {
  const { signup } = useAuth();  // Get signup function from AuthContext
  
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await signup(email, username, password);  // Call AuthContext signup function
      
      // Success! Close modal
      if (onClose) onClose();
      
    } catch (err) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <StyledWrapper>
      <form id="signup-form" onSubmit={handleSubmit}>
        <div className="header-form">
          <span className="title">Create Account</span>
          <span className="subtitle">Join LottoAI today</span>
        </div>

        {error && <div className="error-message">{error}</div>}

        <input 
          type="email" 
          placeholder="Email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required 
          disabled={loading}
        />
        
        <input 
          type="text" 
          placeholder="Username" 
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required 
          disabled={loading}
        />
        
        <input 
          type="password" 
          placeholder="Password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required 
          disabled={loading}
        />
        
        <input 
          type="password" 
          placeholder="Confirm Password" 
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required 
          disabled={loading}
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Sign Up'}
        </button>
        
        <div className="back-to-signin">
          Already have an account?{' '}
          <span 
            className="link" 
            onClick={!loading ? onSwitchToSignIn : undefined}
            style={{ opacity: loading ? 0.5 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
          >
            Sign In
          </span>
        </div>
      </form>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
  #signup-form {
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
    gap: 18px;
  }

  #signup-form .header-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;
  }

  #signup-form .header-form .title {
    font-size: 36px;
    font-weight: bold;
    color: #FFD700;
    margin-bottom: 8px;
  }

  #signup-form .header-form .subtitle {
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

  #signup-form input {
    padding: 14px 18px;
    border: 2px solid rgba(255, 215, 0, 0.3);
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.5);
    color: #FFFFFF;
    font-size: 15px;
    outline: none;
    transition: all 0.3s ease;
  }

  #signup-form input::placeholder {
    color: rgba(229, 229, 229, 0.5);
  }

  #signup-form input:focus {
    border-color: #FFD700;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
  }

  #signup-form input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  #signup-form button[type="submit"] {
    padding: 14px 20px;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    font-size: 15px;
    transition: all 0.3s ease;
    border: none;
    background: #FFD700;
    color: #000;
    box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
    margin-top: 10px;
  }
  
  #signup-form button[type="submit"]:hover:not(:disabled) {
    background: #FFA500;
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(255, 215, 0, 0.4);
  }

  #signup-form button:disabled {
    background: rgba(255, 215, 0, 0.2);
    color: rgba(229, 229, 229, 0.3);
    cursor: not-allowed;
    transform: none;
  }

  #signup-form .back-to-signin {
    text-align: center;
    color: #E5E5E5;
    font-size: 14px;
    margin-top: 10px;
  }

  #signup-form .back-to-signin .link {
    color: #FFD700;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  #signup-form .back-to-signin .link:hover {
    color: #FFA500;
    text-decoration: underline;
  }
`;

export default SignUp_Form;