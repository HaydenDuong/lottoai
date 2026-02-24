function LightRays() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Ray 1 */}
      <div 
        className="absolute light-ray"
        style={{
          left: '10%',
          top: '-50%',
          width: '200px',
          height: '150%',
          background: 'linear-gradient(to bottom, rgba(255, 215, 0, 0.3) 0%, rgba(255, 215, 0, 0.0.8) 50%, transparent 100%)',
          transform: 'rotate(15deg)',
          filter: 'blur(40px)',
        }}
      />
      
      {/* Ray 2 */}
      <div 
        className="absolute light-ray"
        style={{
          left: '35%',
          top: '-50%',
          width: '180px',
          height: '150%',
          background: 'linear-gradient(to bottom, rgba(255, 215, 0, 0.3) 0%, rgba(255, 215, 0, 0.06) 50%, transparent 100%)',
          transform: 'rotate(-5deg)',
          filter: 'blur(50px)',
          animationDelay: '-3s',
        }}
      />
      
      {/* Ray 3 */}
      <div 
        className="absolute light-ray"
        style={{
          left: '60%',
          top: '-50%',
          width: '220px',
          height: '150%',
          background: 'linear-gradient(to bottom, rgba(255, 255, 255, 0.3) 0%, rgba(255, 215, 0, 0.08) 50%, transparent 100%)',
          transform: 'rotate(25deg)',
          filter: 'blur(45px)',
          animationDelay: '-6s',
        }}
      />
      
      {/* Ray 4 */}
      <div 
        className="absolute light-ray"
        style={{
          left: '80%',
          top: '-50%',
          width: '190px',
          height: '150%',
          background: 'linear-gradient(to bottom, rgba(255, 215, 0, 0.3) 0%, rgba(255, 215, 0, 0.05) 50%, transparent 100%)',
          transform: 'rotate(10deg)',
          filter: 'blur(55px)',
          animationDelay: '-9s',
        }}
      />
    </div>
  );
}

export default LightRays;