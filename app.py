import json
import pandas as pd
import numpy as np
import engine
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_catalog(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def get_input(prompt, default, val_type=float):
    user_input = input(f"{prompt} [{default}]: ").strip()
    if not user_input:
        return default
    try:
        return val_type(user_input)
    except ValueError:
        print(f"{Fore.RED}Invalid input. Using default: {default}")
        return default

def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
    print(f"{Fore.CYAN}{Style.BRIGHT} {text}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}\n")

def visualize_curve(theta, n_words, beta, width=50):
    """Simple text-based visualization of theta position in the catalog."""
    pos = int((theta / n_words) * width)
    pos = max(0, min(width - 1, pos))
    bar = ['-'] * width
    bar[pos] = f'{Fore.YELLOW}O{Style.RESET_ALL}'

    left_label = "EASY"
    right_label = "HARD"

    print(f"{left_label} |{''.join(bar)}| {right_label}")
    print(f"{' ' * (len(left_label) + 2 + pos)}{Fore.YELLOW}^ theta={theta:.2f}")

    # Show curve probabilities at key offsets
    offsets = [-200, -100, -50, 0, 50, 100, 200]
    prob_line = "  P(Knows) at relative rank: "
    for offset in offsets:
        x = theta + offset
        p = engine.sigmoid(beta * (theta - x))
        prob_line += f"[{offset:+}]: {p:.2f}  "
    print(f"{Fore.BLACK}{Style.BRIGHT}{prob_line}")

def run_assessment():
    print_header("EvaluationEngine R&D Sandbox")

    vocab_df = load_catalog('cefr_catalog.json')
    n_words = len(vocab_df)

    print(f"Catalog loaded: {n_words} words.")

    # Interactive Hyperparameters
    print(f"{Fore.GREEN}--- Hyperparameter Setup ---")
    eta = get_input("Learning Rate (eta)", 50.0)
    beta = get_input("Sigmoid Slope (beta)", 0.005)
    epsilon = get_input("Convergence Delta (epsilon)", 0.5)
    max_questions = int(get_input("Max Questions", 15))
    initial_theta = get_input("Initial Theta (Rank)", n_words / 2.0)
    ci_decay = get_input("CI Decay Factor", 0.9)

    config = {
        'n_words': n_words,
        'initial_theta': initial_theta,
        'beta': beta,
        'eta': eta,
        'epsilon': epsilon,
        'max_questions': max_questions,
        'ci_decay': ci_decay
    }

    state = engine.initialize_user_state(config)

    print_header("Assessment Phase Started")

    q_count = 0
    converged = False

    while q_count < max_questions:
        q_count += 1
        word = engine.get_next_word(state, vocab_df)

        if not word:
            print(f"{Fore.RED}No more words available!")
            break

        print(f"{Fore.WHITE}{Style.BRIGHT}Question {q_count}/{max_questions}")
        print(f"Word: {Fore.YELLOW}{word['w']}{Style.RESET_ALL} (Rank: {word['rank']})")

        while True:
            choice = input("Do you know this word? (y/n): ").strip().lower()
            if choice in ['y', 'n']:
                known = (choice == 'y')
                break
            print(f"{Fore.RED}Please enter 'y' or 'n'")

        # Update
        update_result = engine.update_user_state(state, word['rank'], known)

        # Verbose Output
        theta_before = state['history'][-1]['theta_before']
        theta_after = update_result['estimated_theta']
        delta = update_result['delta']
        p_known = state['history'][-1]['p_known']

        print(f"\n{Fore.BLUE}Math Trace:")
        print(f"  P(Knows) calculated: {p_known:.4f}")
        print(f"  Theta: {theta_before:.2f} -> {theta_after:.2f} ({Fore.GREEN if delta >=0 else Fore.RED}{delta:+.2f}{Fore.BLUE})")
        print(f"  Confidence Interval: {state['confidence_interval']:.2f}")

        visualize_curve(theta_after, n_words, beta)
        print("-" * 30)

        if update_result['is_converged']:
            print(f"{Fore.GREEN}{Style.BRIGHT}Algorithm converged (delta < epsilon)!")
            converged = True
            break

    print_header("Assessment Results")
    final_theta = state['theta']
    print(f"Final Estimated Theta: {final_theta:.2f}")
    print(f"Total Questions: {q_count}")
    print(f"Status: {'Converged' if converged else 'Max Questions Reached'}")

    # Verification Lists
    print(f"\n{Fore.GREEN}Verification Lists (Empirical 'Knee' check):")

    # 5 words below: Rank - 50 to Rank - 10 (closest to theta)
    below_df = vocab_df[(vocab_df['rank'] >= final_theta - 50) & (vocab_df['rank'] <= final_theta - 10)].tail(5)

    print(f"\n{Fore.YELLOW}Words BELOW Knee (should be mostly known):")
    if below_df.empty:
        print("  None (Too close to start of catalog)")
    for _, row in below_df.iterrows():
        print(f"  - {row['w']} (Rank: {row['rank']})")

    # 5 words above: Rank + 10 to Rank + 50 (closest to theta)
    above_df = vocab_df[(vocab_df['rank'] >= final_theta + 10) & (vocab_df['rank'] <= final_theta + 50)].head(5)

    print(f"\n{Fore.RED}Words ABOVE Knee (should be mostly unknown):")
    if above_df.empty:
        print("  None (Too close to end of catalog)")
    for _, row in above_df.iterrows():
        print(f"  - {row['w']} (Rank: {row['rank']})")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        run_assessment()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Session aborted by user.")
