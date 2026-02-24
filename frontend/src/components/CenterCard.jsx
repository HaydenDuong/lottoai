import Animated_Button from "./Button-Modern";

function CenterCard({ onTryNowClick }) {
  return (
    <div className="bg-black/70 backdrop-blur-xl border-2 border-yellow-400/40 rounded-3xl p-4 max-w-3xl shadow-[0_0_50px_rgba(255,215,0,0.3)]">
      <h2 className="text-3xl font-bold text-yellow-400 mb-4 leading-tight">
        A New Approach to Your Luck
      </h2>
      
      <p className="text-gray-200 text-sm italic mb-4 leading-relaxed">
        Why going through list of prizing numbers when a picture should be enough? 
        LottoAI will extract your ticket number and check for winning prize - 
        simplify the whole process with just a button.
      </p>

      <div className="flex justify-center">
        <Animated_Button onClick={onTryNowClick}>
          TRY NOW
        </Animated_Button>
      </div>
    </div>
  );
}

export default CenterCard;