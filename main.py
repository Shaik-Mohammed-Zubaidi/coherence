from fastapi import FastAPI
from models import BreathCheckIn, BreathResponse
from scoring import calculate_coherence
from memory import store_checkin, get_user_history
from agent import generate_response

app = FastAPI()

@app.post("/breath-check-in", response_model=BreathResponse)
def breath_check_in(data: BreathCheckIn):
    # 1. Store check-in
    store_checkin(data.user_id, data.dict())

    # 2. Calculate coherence score
    score = calculate_coherence(data.breath_rate, data.hrv)

    # 3. Determine trend (bonus)
    history = get_user_history(data.user_id)
    if len(history) >= 3:
        trend_values = [entry['breath_rate'] for entry in history]
        is_rising = all(earlier < later for earlier, later in zip(trend_values, trend_values[1:]))
        trend_info = "User's breath rate has been rising over the last 3 check-ins." if is_rising else None
    else:
        trend_info = None


    # 4. Generate AI response
    response_msg = generate_response(
        data.text,
        score,
        trend=trend_info
    )
    print(f"Generated response: {response_msg} and coherence score: {score}")
    return BreathResponse(coherence_score=score, message=response_msg)
