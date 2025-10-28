import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [baseName, setBaseName] = useState("");
  const [category, setCategory] = useState("");
  const [hasCategory, setHasCategory] = useState(false);
  const [result, setResult] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handlePredict = async () => {
    if (!baseName) return;

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/api/predict", {
        base_name: baseName,
        category: hasCategory ? category : "",
      });
      setResult(res.data.predictions);
    } catch (err) {
      console.error(err);
      setResult([]);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center text-white p-6">
      <h1 className="text-4xl font-bold text-blue-400 mb-4">
        Predict the TLD
      </h1>

      <div className="bg-gray-800 p-6 rounded-xl shadow-lg w-full max-w-lg">
        <input
          type="text"
          placeholder="Enter base name (e.g. github)"
          value={baseName}
          onChange={(e) => setBaseName(e.target.value)}
          className="w-full p-3 mb-4 bg-gray-700 rounded-lg text-white"
        />

        <div className="flex items-center mb-3">
          <input
            type="checkbox"
            checked={hasCategory}
            onChange={(e) => setHasCategory(e.target.checked)}
            className="mr-2"
          />
          <label>Do you know this website's category?</label>
        </div>

        {hasCategory && (
          <input
            type="text"
            placeholder="Enter category (e.g. computers)"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full p-3 mb-4 bg-gray-700 rounded-lg text-white"
          />
        )}

        <button
          onClick={handlePredict}
          disabled={loading}
          className="w-full bg-blue-500 hover:bg-blue-600 py-2 rounded-lg font-semibold"
        >
          {loading ? "Predicting..." : "Predict TLD"}
        </button>

        {result.length > 0 && (
          <div className="mt-6 text-center">
            <h2 className="text-xl font-semibold mb-2">Top Predictions:</h2>
            {result.map((r, i) => (
              <p key={i} className="text-gray-300">
                {i + 1}. <span className="text-blue-400">.{r.tld}</span>{" "}
                ({(r.score * 100).toFixed(1)}%)
              </p>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={() => navigate("/game")}
        className="mt-8 bg-green-500 hover:bg-green-600 py-3 px-8 rounded-xl text-lg font-semibold"
      >
        Play the Game →
      </button>
    </div>
  );
}
