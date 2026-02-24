import { motion } from 'framer-motion';

function ProcessBox({ icon, label, controls }) {
  return (
    <motion.div
      animate={controls}
      initial={{ opacity: 0, scale: 0.8 }}
      className="bg-black/70 backdrop-blur-md border-2 border-yellow-400/40 rounded-xl p-4 w-28 h-28 flex flex-col items-center justify-center shadow-[0_0_30px_rgba(255,215,0,0.2)] hover:shadow-[0_0_40px_rgba(255,215,0,0.4)] transition-shadow"
    >
      <div className="text-3xl mb-1">{icon}</div>
      <h3 className="text-yellow-400 font-bold text-xs">{label}</h3>
    </motion.div>
  );
}

export default ProcessBox;