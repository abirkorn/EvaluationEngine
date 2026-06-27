import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import engine
from typing import List, Dict, Any, Optional

app = FastAPI(title="EvaluationEngine R&D Sandbox")

# Load catalog globally
VOCAB_DF = pd.read_json('cefr_catalog.json')
N_WORDS = len(VOCAB_DF)

class InitConfig(BaseModel):
    eta: float = 50.0
    beta: float = 0.005
    epsilon: float = 0.5
    max_questions: int = 15
    initial_theta: Optional[float] = None
    ci_decay: float = 0.9

class StateRequest(BaseModel):
    user_state: Dict[str, Any]

class RespondRequest(BaseModel):
    user_state: Dict[str, Any]
    word_rank: int
    is_known: bool

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/init")
async def init_session(config: InitConfig):
    initial_theta = config.initial_theta if config.initial_theta is not None else N_WORDS / 2.0
    engine_config = {
        'n_words': N_WORDS,
        'initial_theta': initial_theta,
        'beta': config.beta,
        'eta': config.eta,
        'epsilon': config.epsilon,
        'max_questions': config.max_questions,
        'ci_decay': config.ci_decay
    }
    state = engine.initialize_user_state(engine_config)
    return state

@app.post("/next-word")
async def next_word(req: StateRequest):
    word = engine.get_next_word(req.user_state, VOCAB_DF)
    return word

@app.post("/respond")
async def respond(req: RespondRequest):
    update_result = engine.update_user_state(req.user_state, req.word_rank, req.is_known)

    # Check if max questions reached
    q_count = len(update_result['state']['history'])
    max_q = update_result['state']['config'].get('max_questions', 15)

    if q_count >= max_q:
        update_result['is_converged'] = True # Force termination

    if update_result['is_converged']:
        # Add verification lists
        final_theta = update_result['estimated_theta']
        below_df = VOCAB_DF[(VOCAB_DF['rank'] >= final_theta - 50) & (VOCAB_DF['rank'] <= final_theta - 10)].tail(5)
        above_df = VOCAB_DF[(VOCAB_DF['rank'] >= final_theta + 10) & (VOCAB_DF['rank'] <= final_theta + 50)].head(5)

        update_result['verification'] = {
            'below': below_df.to_dict(orient='records'),
            'above': above_df.to_dict(orient='records')
        }

    return update_result

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
