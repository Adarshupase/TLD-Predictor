import { useEffect, useState } from "react";
import axios from "axios";

export default function App() {
  const [question, setQuestion] = useState(null);
  const [selected, setSelected] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchQuestion = async () => {
    setLoading(true);
    try {
      const res = await axios.get("http://localhost:5000/api/question");
      setQuestion(res.data);
      setSelected(null);
      setFeedback("");
    } catch (err) {
      console.error(err);
      setFeedback("⚠️ Could not load question. Is backend running?");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchQuestion();
  }, []);

  const handleGuess = (tld) => {
    if (selected) return; // prevent double click
    setSelected(tld);

    if (tld === question.answer) {
      setFeedback("✅ Correct!");
      setScore(score + 10);
      setStreak(streak + 1);
    } else {
      setFeedback(`❌ Wrong! Correct was .${question.answer}`);
      setStreak(0);
    }
  };

  const nextQuestion = () => {
    fetchQuestion();
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-screen bg-gray-900 text-white text-xl">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-400 mb-4"></div>
        <p>Loading Question...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col justify-center items-center text-white font-sans p-4">
      <div className="bg-gray-800/80 rounded-2xl shadow-lg p-8 w-full max-w-md border border-gray-700">
        <h1 className="text-3xl font-bold mb-2 text-center text-blue-400">
          🌐 Guess the TLD!
        </h1>
        <p className="text-center text-gray-400 mb-6">
          So you're a web developer? name every webite.
        </p>

        <div className="text-center mb-6">
          <p className="text-xl font-semibold">
            <span className="text-gray-400">Domain:</span> {question.domain}
          </p>
          <p className="text-lg text-gray-300">
            <span className="text-gray-400">Category:</span> {question.category}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {question.options.map((opt) => (
            <button
              key={opt}
              onClick={() => handleGuess(opt)}
              disabled={!!selected}
              className={`py-2 px-4 rounded-lg text-lg font-semibold transition-all duration-200 border
                ${
                  selected
                    ? opt === question.answer
                      ? "bg-green-500 border-green-400"
                      : opt === selected
                      ? "bg-red-500 border-red-400"
                      : "bg-gray-700 border-gray-600"
                    : "bg-gray-700 hover:bg-gray-600 hover:border-blue-400 border-gray-700"
                }`}
            >
              .{opt}
            </button>
          ))}
        </div>

        {feedback && (
          <p
            className={`text-center mt-5 text-xl font-medium ${
              feedback.startsWith("✅")
                ? "text-green-400"
                : feedback.startsWith("❌")
                ? "text-red-400"
                : "text-yellow-400"
            }`}
          >
            {feedback}
          </p>
        )}

        <div className="flex justify-between mt-6 text-gray-300">
          <p>🏆 Score: <span className="text-white font-semibold">{score}</span></p>
          <p>🔥 Streak: <span className="text-white font-semibold">{streak}</span></p>
        </div>

        <button
          onClick={nextQuestion}
          className="w-full mt-6 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg shadow transition duration-200"
        >
          Next Question →
        </button>
      </div>

      
    </div>
  );
}
