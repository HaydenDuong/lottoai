import styled from 'styled-components';

const Underline_Text = ({children, href}) => {
  return (
    <StyledWrapper>
        <a href={href}>
            {children}
        </a>
    </StyledWrapper>
  );
}

const StyledWrapper = styled.div`
    a {
        font-size: 18px;
        color: #e1e1e1;
        font-family: inherit;
        font-weight: 400;
        cursor: pointer;
        position: relative;
        border: none;
        background: none;
        text-transform: uppercase;
        text-decoration: none;
        display: inline-block;
        transition-timing-function: cubic-bezier(0.25, 0.8, 0.25, 1);
        transition-duration: 400ms;
        transition-property: color;
    }

    a:focus,
    a:hover {
        color: #FFD700;
    }

    a:focus:after,
    a:hover:after {
        width: 100%;
        left: 0%;
    }

    a:after {
        content: "";
        pointer-events: none;
        bottom: -2px;
        left: 50%;
        position: absolute;
        width: 0%;
        height: 2px;
        background-color: #FFD700;
        transition-timing-function: cubic-bezier(0.25, 0.8, 0.25, 1);
        transition-duration: 400ms;
        transition-property: width, left;
    }
`;

export default Underline_Text;
