import requests
import threading

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT  = 120   # seconds — first run loads the model into RAM, needs more time


class OllamaAI:
    """Interface for local Ollama LLM using the HTTP API (no subprocess)."""

    def __init__(self, model_name="llama2"):
        self.model_name = model_name

    # ------------------------------------------------------------------
    # Availability checks
    # ------------------------------------------------------------------
    def is_available(self):
        """Return True if the Ollama HTTP server is reachable."""
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return r.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def is_model_available(self, model_name=None):
        """Return True if the requested model has been pulled locally."""
        if model_name is None:
            model_name = self.model_name
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                # Match on base name so "llama2" matches "llama2:latest" etc.
                return any(model_name in m for m in models)
            return False
        except requests.exceptions.RequestException:
            return False

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------
    def analyze_skin_condition(self, skin_condition, confidence, user_context, db=None):
        """
        Get AI analysis via the Ollama HTTP API (non-streaming).

        Args:
            skin_condition : str   – "Acne", "Clear", or "Dark Circles"
            confidence     : float – model confidence (0–1)
            user_context   : str   – user-provided context about their skin/situation
            db             : Database | None – if provided, saves result to Supabase

        Returns:
            str – AI analysis text
        """
        if not self.is_model_available():
            return f"Error: Model '{self.model_name}' not found. Run: ollama pull {self.model_name}"

        prompt = (
            f"You are a helpful skincare advisor analyzing a skin condition detection result.\n\n"
            f"Model Detection: {skin_condition}\n"
            f"Confidence: {confidence:.0%}\n"
            f"User Context: {user_context}\n\n"
            f"Based on the model's detection and the user's context, provide:\n"
            f"1. A brief assessment of the detected condition\n"
            f"2. How the user's context might be relevant\n"
            f"3. 2-3 specific recommendations for skincare or next steps\n\n"
            f"Keep your response concise and practical (2-3 sentences max)."
        )

        try:
            r = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model":  self.model_name,
                    "prompt": prompt,
                    "stream": False,          # wait for full response
                },
                timeout=OLLAMA_TIMEOUT,
            )
            r.raise_for_status()
            response = r.json().get("response", "").strip()

            if not response:
                return "Unable to get response from Ollama"

            # Persist to Supabase if a db handle was supplied
            if db is not None:
                try:
                    db.insert_ollama_advice(
                        result_text=response,
                        model_result=skin_condition,
                        model_confidence=confidence,
                    )
                except Exception as db_err:
                    print(f"[DB] Failed to save Ollama advice: {db_err}")

            return response

        except requests.exceptions.Timeout:
            return "Error: Ollama took too long to respond — try a smaller model (e.g. mistral)"
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama — is it running? (ollama serve)"
        except Exception as e:
            return f"Error analyzing with AI: {str(e)}"

    # ------------------------------------------------------------------
    # Non-blocking wrapper
    # ------------------------------------------------------------------
    def analyze_async(self, skin_condition, confidence, user_context, callback, db=None):
        """
        Run analyze_skin_condition in a background thread.

        Args:
            callback : callable(str) – called with the result when done
        """
        def _run():
            result = self.analyze_skin_condition(skin_condition, confidence, user_context, db=db)
            callback(result)

        t = threading.Thread(target=_run, daemon=True)
        t.start()