import styled from 'styled-components';

const Button = ({children, onClick}) => {
  return (
    <StyledWrapper>
      <button className="button" onClick={onClick}>{children}</button>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
  .button {
    padding: 1em 1em;
    border: none;
    border-radius: 5px;
    font-weight: bold;
    letter-spacing: 5px;
    text-transform: uppercase;
    cursor: pointer;
    color: #ffffffff;
    transition: all 1000ms;
    font-size: 13px;
    position: relative;
    overflow: hidden;
    outline: 2px solid #ffffffff;
  }

  button:hover {
    color: #FFD700;
    transform: scale(1.1);
    outline: 2px solid #000000ff;
    box-shadow: 4px 5px 17px -4px #000000ff;
  }

  button::before {
    content: "";
    position: absolute;
    left: -50px;
    top: 0;
    width: 0;
    height: 100%;
    background-color: #0c0c0dff;
    transform: skewX(45deg);
    z-index: -1;
    transition: width 1000ms;
  }

  button:hover::before {
    width: 250%;
  }
`;

export default Button;
