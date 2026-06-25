import numpy as np
import pandas as pd

def sigmoid(z):
    """Standard logistic function."""
    # Use clip to avoid overflow in exp
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))

def initialize_user_state(config: dict) -> dict:
    """
    Set up the initial state structure (theta, variance/confidence, history logs).

    Config keys:
    - n_words: Total number of words in catalog
    - initial_theta: Initial placement (default: middle of catalog)
    - initial_ci: Initial confidence interval (default: n_words)
    - beta: Sigmoid slope (discrimination parameter)
    - eta: Learning rate
    - epsilon: Convergence delta
    - max_questions: Maximum questions for assessment
    """
    n_words = config.get('n_words', 5000)
    state = {
        'theta': config.get('initial_theta', n_words / 2.0),
        'confidence_interval': config.get('initial_ci', float(n_words)),
        'history': [],
        'config': config
    }
    return state

def get_next_word(user_state: dict, vocab_df: pd.DataFrame) -> dict:
    """
    Select the next optimal word focusing on the area of maximum uncertainty (P approx 0.5).
    Excludes words already presented in the current session.
    """
    theta = user_state['theta']
    # history records word_id (which we treat as rank here)
    seen_ids = [h['word_id'] for h in user_state['history']]

    available_words = vocab_df[~vocab_df['rank'].isin(seen_ids)]

    if available_words.empty:
        return None

    # Find word with rank closest to theta
    # We use rank as the continuous difficulty index x
    idx = (available_words['rank'] - theta).abs().idxmin()
    word = available_words.loc[idx].to_dict()
    return word

def update_user_state(user_state: dict, word_id: int, is_known: bool) -> dict:
    """
    Perform the mathematical update using the online gradient step.
    Returns the updated state and transition details.
    """
    theta_prev = user_state['theta']
    config = user_state['config']

    beta = config.get('beta', 0.01)
    eta = config.get('eta', 0.1)
    epsilon = config.get('epsilon', 0.5)
    ci_decay = config.get('ci_decay', 0.9)

    # x is the continuous rank of the word
    x = float(word_id)
    y = 1.0 if is_known else 0.0

    # P(Knows x | theta, beta) = sigma(beta * (theta - x))
    p_known = sigmoid(beta * (theta_prev - x))

    # SGD Update: theta_t = theta_{t-1} + eta * (y_t - P(x_t))
    delta = eta * (y - p_known)
    theta_new = theta_prev + delta

    # Update state
    user_state['theta'] = theta_new
    user_state['confidence_interval'] *= ci_decay
    user_state['history'].append({
        'word_id': word_id,
        'rank': x,
        'known': is_known,
        'p_known': p_known,
        'delta': delta,
        'theta_before': theta_prev,
        'theta_after': theta_new
    })

    is_converged = abs(delta) < epsilon

    return {
        'state': user_state,
        'estimated_theta': theta_new,
        'delta': delta,
        'is_converged': is_converged
    }

def update_user_state_passive(user_state: dict, chapter_exposures: list) -> dict:
    """
    Consumes passive signals from reading exposures and clicks.
    chapter_exposures: list of dicts with {word_id, exposures, clicks}
    """
    theta = user_state['theta']
    config = user_state['config']

    beta = config.get('beta', 0.01)
    eta = config.get('eta', 0.1)
    alpha_smooth = config.get('alpha_smooth', 1.0)
    beta_smooth = config.get('beta_smooth', 2.0)

    total_delta = 0.0
    updates = []

    for entry in chapter_exposures:
        x = float(entry['word_id'])
        e_x = float(entry['exposures'])
        c_x = float(entry['clicks'])

        # Laplace Smoothing: P_hat = 1 - (Cx + alpha) / (Ex + beta_smooth)
        p_hat = 1.0 - (c_x + alpha_smooth) / (e_x + beta_smooth)

        # Model prediction
        p_model = sigmoid(beta * (theta - x))

        # Gradient update
        delta = eta * (p_hat - p_model)
        theta += delta
        total_delta += delta

        updates.append({
            'word_id': entry['word_id'],
            'p_hat': p_hat,
            'p_model': p_model,
            'delta': delta
        })

    user_state['theta'] = theta
    return {
        'state': user_state,
        'estimated_theta': theta,
        'total_delta': total_delta,
        'updates': updates
    }
