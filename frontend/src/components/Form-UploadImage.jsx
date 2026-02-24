import React, { useState } from 'react';
import styled from 'styled-components';
import { useAuth } from '../hooks/useAuth';

const Form = () => {
  const { token, user } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setResult(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Build headers - including Authorization if user is logged in
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('http://127.0.0.1:8000/upload/', {
        method: 'POST',
        headers: headers,
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.message || 'Upload failed');
      }
    } catch (err) {
      setError(`Network error: ${err.message || 'Please check if the backend is running.'}`);
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  // Prize tier names mapping
  const prizeTierNames = {
    'jp': 'Jackpot 🎉',
    'jp-consolation': 'Jackpot Consolation',
    '1': '1st Prize',
    '2': '2nd Prize',
    '3': '3rd Prize',
    '4': '4th Prize',
    '5': '5th Prize',
    '6': '6th Prize',
    '7': '7th Prize',
    '8': '8th Prize'
  };

  return (
    <StyledWrapper>
      <div className="container">
        
        {/* File Selection Area */}
        {!result && (
          <>
            <div className="header" onClick={() => document.getElementById('file').click()}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g id="SVGRepo_bgCarrier" strokeWidth={0} />
                <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round" />
                <g id="SVGRepo_iconCarrier">
                  <path d="M7 10V9C7 6.23858 9.23858 4 12 4C14.7614 4 17 6.23858 17 9V10C19.2091 10 21 11.7909 21 14C21 15.4806 20.1956 16.8084 19 17.5M7 10C4.79086 10 3 11.7909 3 14C3 15.4806 3.8044 16.8084 5 17.5M7 10C7.43285 10 7.84965 10.0688 8.24006 10.1959M12 12V21M12 12L15 15M12 12L9 15" stroke="#FFD700" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </g>
              </svg>
              {preview ? (
                <img src={preview} alt="Preview" className="preview-image" />
              ) : (
                <p>Click or Browse File to upload!</p>
              )}
            </div>

            <label htmlFor="file" className="footer">
              <svg fill="#FFD700" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                <g id="SVGRepo_bgCarrier" strokeWidth={0} />
                <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round" />
                <g id="SVGRepo_iconCarrier">
                  <path d="M15.331 6H8.5v20h15V14.154h-8.169z" />
                  <path d="M18.153 6h-.009v5.342H23.5v-.002z" />
                </g>
              </svg>
              <p>{selectedFile ? selectedFile.name : 'No file selected'}</p>
              {selectedFile && (
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" onClick={handleReset}>
                  <g id="SVGRepo_bgCarrier" strokeWidth={0} />
                  <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round" />
                  <g id="SVGRepo_iconCarrier">
                    <path d="M5.16565 10.1534C5.07629 8.99181 5.99473 8 7.15975 8H16.8402C18.0053 8 18.9237 8.9918 18.8344 10.1534L18.142 19.1534C18.0619 20.1954 17.193 21 16.1479 21H7.85206C6.80699 21 5.93811 20.1954 5.85795 19.1534L5.16565 10.1534Z" stroke="#FFD700" strokeWidth={2} />
                    <path d="M19.5 5H4.5" stroke="#FFD700" strokeWidth={2} strokeLinecap="round" />
                    <path d="M10 3C10 2.44772 10.4477 2 11 2H13C13.5523 2 14 2.44772 14 3V5H10V3Z" stroke="#FFD700" strokeWidth={2} />
                  </g>
                </svg>
              )}
            </label>

            <input id="file" type="file" accept=".jpg,.jpeg" onChange={handleFileChange} />

            {/* Upload Button */}
            {selectedFile && (
              <button className="upload-btn" onClick={handleUpload} disabled={loading}>
                {loading ? 'Processing...' : 'Check My Ticket'}
              </button>
            )}

            {/* Error Message */}
            {error && <div className="error-message">{error}</div>}
          </>
        )}

        {/* Results Display */}
        {result && result.prize_check && (
          <div className="results">
            <h2 className="results-title">🎫 Results</h2>
            
            {/* Guest user notice */}
            {!user && (
              <div className="guest-notice">
                ℹ️ You're checking as a guest. <strong>Sign in</strong> to save your numbers!
              </div>
            )}

            {/* Saved confirmation for logged-in users */}
            {user && (
              <div className="saved-notice">
                ✅ Number saved to your account!
              </div>
            )}

            <div className="extracted-number">
              <p className="label">Your Number:</p>
              <p className="number">{result.extracted_digits || result.prize_check.user_number}</p>
            </div>

            <div className="prize-status">
              {result.prize_check.is_winner ? (
                <>
                  <div className="winner-badge">🎉 WINNER! 🎉</div>
                  <div className="prizes-list">
                    <p className="prizes-label">Matched Prizes:</p>
                    {result.prize_check.matched_prizes.map((prize, index) => (
                      <div key={index} className="prize-item">
                        {prizeTierNames[prize] || `Prize ${prize}`}
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="no-win-badge">Not a winner this time. Try again!</div>
              )}
            </div>

            <div className="draw-info">
              <p>Draw Date: <span>{result.prize_check.draw_info.draw_date}</span></p>
              <p>Region: <span>{result.prize_check.draw_info.region.toUpperCase()}</span></p>
            </div>

            <button className="reset-btn" onClick={handleReset}>
              Check Another Ticket
            </button>
          </div>
        )}
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  .container {
    min-height: 350px;
    width: 450px;
    max-width: 95vw;
    border-radius: 16px;
    box-shadow: 0 0 50px rgba(255, 215, 0, 0.3);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 20px;
    gap: 15px;
    background-color: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(255, 215, 0, 0.4);
  }

  .header {
    flex: 1;
    width: 100%;
    min-height: 180px;
    border: 2px dashed #FFD700;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }

  .header:hover {
    border-color: #FFA500;
    background-color: rgba(255, 215, 0, 0.05);
  }

  .header svg {
    height: 80px;
    filter: invert(87%) sepia(61%) saturate(561%) hue-rotate(359deg) brightness(103%) contrast(103%);
  }

  .preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 8px;
  }

  .header p {
    text-align: center;
    color: #FFD700;
    font-weight: 600;
    margin-top: 10px;
  }

  .footer {
    background-color: rgba(255, 215, 0, 0.1);
    width: 100%;
    height: 50px;
    padding: 10px;
    border-radius: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    color: #E5E5E5;
    border: 1px solid rgba(255, 215, 0, 0.3);
    transition: all 0.3s ease;
    gap: 10px;
  }

  .footer:hover {
    background-color: rgba(255, 215, 0, 0.2);
    border-color: #FFD700;
  }

  .footer svg {
    height: 24px;
    width: 24px;
    fill: #FFD700;
    flex-shrink: 0;
  }

  .footer p {
    flex: 1;
    text-align: center;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  #file {
    display: none;
  }

  .upload-btn, .reset-btn {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #000;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
  }

  .upload-btn:hover, .reset-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5);
  }

  .upload-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .error-message {
    width: 100%;
    padding: 10px;
    background-color: rgba(255, 0, 0, 0.1);
    border: 1px solid rgba(255, 0, 0, 0.3);
    border-radius: 8px;
    color: #ff6b6b;
    text-align: center;
    font-size: 14px;
  }

  /* Results Styles */
  .results {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 15px;
    animation: fadeIn 0.5s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .results-title {
    color: #FFD700;
    text-align: center;
    font-size: 24px;
    margin: 0;
    font-weight: 700;
  }

  .extracted-number {
    background: rgba(255, 215, 0, 0.1);
    border: 2px solid rgba(255, 215, 0, 0.3);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
  }

  .extracted-number .label {
    color: #E5E5E5;
    font-size: 14px;
    margin: 0 0 8px 0;
  }

  .extracted-number .number {
    color: #FFD700;
    font-size: 32px;
    font-weight: 700;
    margin: 0;
    letter-spacing: 4px;
  }

  .prize-status {
    background: rgba(255, 215, 0, 0.05);
    border-radius: 10px;
    padding: 15px;
  }

  .winner-badge {
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #000;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 15px;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }

  .no-win-badge {
    background: rgba(255, 255, 255, 0.1);
    color: #E5E5E5;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
    font-size: 16px;
  }

  .prizes-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .prizes-label {
    color: #FFD700;
    font-weight: 600;
    margin: 0 0 5px 0;
  }

  .prize-item {
    background: rgba(255, 215, 0, 0.15);
    border-left: 3px solid #FFD700;
    padding: 10px;
    border-radius: 5px;
    color: #E5E5E5;
    font-weight: 500;
  }

  .draw-info {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    color: #E5E5E5;
  }

  .draw-info p {
    margin: 5px 0;
  }

  .draw-info span {
    color: #FFD700;
    font-weight: 600;
  }
  
  .guest-notice {
    background: rgba(255, 165, 0, 0.1);
    border: 1px solid rgba(255, 165, 0, 0.3);
    border-radius: 8px;
    padding: 12px;
    color: #FFA500;
    font-size: 14px;
    text-align: center;
    margin-bottom: 15px;
  }

  .guest-notice strong {
    color: #FFD700;
  }

  .saved-notice {
    background: rgba(0, 255, 0, 0.1);
    border: 1px solid rgba(0, 255, 0, 0.3);
    border-radius: 8px;
    padding: 12px;
    color: #00ff00;
    font-size: 14px;
    text-align: center;
    margin-bottom: 15px;
  }
`;

export default Form;