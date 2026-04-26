import cv2
import time
import os
import threading
from model import SkinModel
from ollama_helper import OllamaAI
from tts_helper import PiperTTS
from database import Database

class_names = ["Acne", "Clear", "Dark Circles"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def wrap_text(text, width=40):
    words = text.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + " " + word) <= width:
            current_line += " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # ── Camera ──────────────────────────────────────────────────────────────
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available")
        return

    ret, frame = cap.read()
    if ret:
        cv2.putText(frame, "Initializing Skin Scanner...", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, "Loading AI, TTS, and Database...", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        cv2.imshow("Skin Scanner", frame)
        cv2.waitKey(500)

    # ── Components ──────────────────────────────────────────────────────────
    model = SkinModel("skin_model_weights.pth")
    ai    = OllamaAI(model_name="llama2")
    tts   = PiperTTS()

    db = None
    try:
        db = Database()
        db_status = "Database: Connected"
    except Exception as e:
        print(f"[DB] Connection failed: {e}")
        db_status = f"Database: Failed ({e})"

    status_messages = [db_status]

    if not ai.is_available():
        status_messages.append("Ollama: Not running (start with: ollama serve)")
        ai = None
    elif not ai.is_model_available():
        status_messages.append(f"Ollama model '{ai.model_name}' not found")
        ai = None
    else:
        status_messages.append("AI: Ready")

    if not tts.is_available():
        status_messages.append("TTS: Not available")
        tts = None
    else:
        status_messages.append("TTS: Ready")

    ret, frame = cap.read()
    if ret:
        y_pos = 50
        for msg in status_messages:
            color = (0, 255, 0) if "Failed" not in msg and "not" not in msg.lower() else (0, 100, 255)
            cv2.putText(frame, msg, (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_pos += 40
        cv2.putText(frame, "Press any key to start...", (50, y_pos + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.imshow("Skin Scanner", frame)
        cv2.waitKey(2000)

    # ── State ────────────────────────────────────────────────────────────────
    user_id          = 1
    last_saved_time  = 0
    interval         = 5
    last_saved_label = None
    image_folder     = "images"
    os.makedirs(image_folder, exist_ok=True)

    current_analysis    = ""
    awaiting_context    = False
    context_input       = ""
    last_detection_time = 0
    ai_busy             = False   # True while background analysis is running

    last_label      = "Unsure"
    last_confidence = 0.0

    # Thread-safe result bucket: the callback writes here, main loop reads it
    ai_result_bucket = {"text": None}
    result_lock      = threading.Lock()

    def on_ai_done(text):
        with result_lock:
            ai_result_bucket["text"] = text

    # ── Main loop ────────────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        pred_index, confidence = model.predict(frame)
        label        = class_names[pred_index] if confidence >= 0.7 else "Unsure"
        current_time = time.time()

        last_label      = label
        last_confidence = confidence

        # ── Check if background AI finished ─────────────────────────────────
        with result_lock:
            finished_text = ai_result_bucket["text"]
            if finished_text is not None:
                ai_result_bucket["text"] = None
                ai_busy = False
                wrapped          = wrap_text(finished_text, width=40)
                current_analysis = f"AI Analysis:\n{wrapped}"
                if tts:
                    # Run TTS in its own thread too so it doesn't block
                    threading.Thread(target=tts.speak, args=(finished_text,), daemon=True).start()

        # ── Save / detect new condition ──────────────────────────────────────
        if (
            confidence >= 0.7
            and (current_time - last_saved_time > interval)
            and (label != last_saved_label)
            and not ai_busy          # don't stack analyses
        ):
            timestamp = int(current_time)
            filename  = f"{image_folder}/scan_{timestamp}.jpg"
            cv2.imwrite(filename, frame)

            if db is not None:
                try:
                    db.insert_scan(user_id, label, confidence, filename)
                except Exception as e:
                    print(f"[DB] insert_scan failed: {e}")

            if ai and label != "Unsure":
                awaiting_context = True
                context_input    = ""
                current_analysis = f"Detected: {label} ({confidence:.2f})"
            else:
                current_analysis = f"Saved: {label} ({confidence:.2f})"

            last_saved_time     = current_time
            last_saved_label    = label
            last_detection_time = current_time

        # ── Keyboard input ───────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if awaiting_context:
            if key == 13:  # Enter – kick off async analysis
                user_context     = context_input.strip() or "No additional context provided."
                current_analysis = "Analyzing with AI... (camera stays live)"
                awaiting_context = False
                ai_busy          = True

                ai.analyze_async(
                    last_label, last_confidence, user_context,
                    callback=on_ai_done,
                    db=db,
                )

            elif key == 8:  # Backspace
                context_input = context_input[:-1]
            elif 32 <= key <= 126:
                context_input += chr(key)
            elif key == 27:  # Escape – skip
                awaiting_context = False
                current_analysis = f"Saved: {last_label} ({last_confidence:.2f})"

        # ── On-screen text ───────────────────────────────────────────────────
        cv2.putText(frame, f"{label} ({confidence:.2f})", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        y_offset = 70
        if awaiting_context:
            cv2.putText(frame, "Enter context (or Enter to skip):", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            y_offset += 25
            cv2.putText(frame, f"Context: {context_input}", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
            cv2.putText(frame, "e.g. 'stressed lately', 'new routine'", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        elif ai_busy:
            cv2.putText(frame, "AI thinking...", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
        elif current_analysis:
            for line in current_analysis.split("\n"):
                cv2.putText(frame, line, (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 20
            # Hint to restart once analysis is shown
            cv2.putText(frame, "Press 'r' to scan again", (10, y_offset + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        elif current_time - last_detection_time > 3:
            for instruction in ["Controls:", "'a' - Manual analysis", "'r' - Restart scan", "'q' - Quit"]:
                cv2.putText(frame, instruction, (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                y_offset += 20

        # ── Restart scan ─────────────────────────────────────────────────────
        if key == ord("r") and not awaiting_context and not ai_busy:
            current_analysis    = ""
            last_saved_label    = None  # allow same condition to trigger again
            last_saved_time     = 0
            last_detection_time = 0

        # ── Manual analysis ──────────────────────────────────────────────────
        if key == ord("a") and not awaiting_context and not ai_busy:
            if ai and label != "Unsure":
                awaiting_context = True
                context_input    = ""
                current_analysis = f"Manual analysis: {label} ({confidence:.2f})"
            else:
                current_analysis = "AI not available for analysis"

        if key == ord("q"):
            break

        cv2.imshow("Skin Scanner", frame)

    # ── Cleanup ──────────────────────────────────────────────────────────────
    cap.release()
    if db is not None:
        db.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()