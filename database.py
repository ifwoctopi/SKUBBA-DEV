import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class Database:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file")

        self.client: Client = create_client(url, key)

    # ------------------------------------------------------------------
    # scans table
    # ------------------------------------------------------------------
    def insert_scan(self, user_id, label, confidence, image_path=None):
        """Insert a row into public.scans and return the new scan_id."""
        response = (
            self.client.table("scans")
            .insert({
                "user_id":         user_id,
                "predicted_label": label,
                "confidence":      confidence,
                "image_path":      image_path,
            })
            .execute()
        )
        return response.data[0]["scan_id"] if response.data else None

    # ------------------------------------------------------------------
    # ollama_advice table
    # ------------------------------------------------------------------
    def insert_ollama_advice(self, result_text, model_result, model_confidence):
        """Insert a row into public.ollama_advice and return the new result_id."""
        response = (
            self.client.table("ollama_advice")
            .insert({
                "result":           result_text,
                "model_result":     model_result,
                "model_confidence": model_confidence,
            })
            .execute()
        )
        return response.data[0]["result_id"] if response.data else None

    # ------------------------------------------------------------------
    def close(self):
        # supabase-py manages its own HTTP session; nothing to close manually.
        pass