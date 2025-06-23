import os 
import random
import google.generativeai as gen
from dotenv import load_dotenv
from rich import print as rprint
from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console

from core.crisis import CRISES
from core.advisor import Council
from core.stats import apply_policy, print_stats, generate_sample_policy_deltas


load_dotenv()
gen.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GameState:
    def __init__(self):
        self.treasury = 70
        self.stability = 70
        self.popularity = 60 
        self.army = 65 
        self.turn = 0
    
    def to_dict(self):
        return {
            "treasury": self.treasury,
            "stability": self.stability,
            "popularity": self.popularity,
            "army": self.army,
            "turn": self.turn
        }


def print_player_commands():
    console = Console()
    console.print(Panel.fit(
        "[bold yellow]Player Commands[/bold yellow]\n\n"
        "[cyan]ask [advisor name] [message][/cyan]                        - Ask a single advisor something\n"
        "[cyan]all [message][/cyan]                        - Broadcast a message to all advisors\n"
        "[cyan]!choose [alloc_A] [alloc_B] [alloc_C][/cyan]                        - Lock in policy allocations (e.g., !choose 50 30 20)\n"
        "[cyan]log[/cyan]                        - Show the conversation history\n"
        "[cyan]quit[/cyan]                        - End the game immediately\n\n"
        "[dim italic]Example: !choose 60 20 20 (allocates 60% to A, 20% to B, 20% to C)[/dim italic]",
        title="How to Play",
        border_style="bright_blue"
    ))


async def game_loop():
    state = GameState()
    council = Council()
    console = Console()

    model = gen.GenerativeModel("gemini-2.5-flash-preview-05-20")
    gen.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    rprint(Panel("Welcome, ruler. Your reign begins now.", title="Counsel"))
    rprint("You have the following kingdom stats:")
    print_stats(state)
    rprint("Type \"Help\" for a list of commands.\n")

    thread = [] 

    while state.turn < 6:
        crisis_text, options = random.choice(CRISES)
        # = CRISES[state.turn % len(CRISES)] <- determinstic crisis selection 
        state.turn += 1
        num_options = len(options)

        current_turn_policy_base_effects = [generate_sample_policy_deltas() for _ in options]

        rprint(f"\n[bold yellow]Crisis {state.turn}:[/] {crisis_text}")
        rprint("You have the following policy options:")
        for i, option in enumerate(options, start=65):
            rprint(f"  [bold]{chr(i)}[/]: {option}")

        rprint("\n[italic]Your advisors are deliberating...[/]\n")

        # get each advisor's response 
        advice = await council.consult(model, crisis_text,
        options, state.to_dict(), thread, 
        current_turn_policy_base_effects)
        for name, response in advice: 
            if response != "...":
                rprint(f"[bright_cyan]{name}[/]: {response}")
                thread.append(f"{name}: {response}")
        
        # wait for player input on allocations
        chosen_allocations = None
        while not chosen_allocations:
            command = Prompt.ask("\n[white]>[/]")

            if command.lower() == "help":
                print_player_commands()
                continue

            if command.startswith("ask "):
                parts = command.split()
                if len(parts) < 4 or not parts[2].isdigit():
                    rprint("[red]Invalid format. Use: ask Advisor [number] [message][/]\n[dim]Example: ask Advisor 1 What are the risks of policy A?[/dim]")
                    continue
                advisor_name = f"{parts[1]} {parts[2]}"
                msg = " ".join(parts[3:])
                thread.append(f"Player to {advisor_name}: {msg}")

                found = False
                for advisor in council.advisors:
                    if advisor.name.lower() == advisor_name.lower():
                        # Pass policy_base_effects_list to individual advisor queries too
                        reply = await advisor.advise(model, crisis_text, options, state.to_dict(), thread, current_turn_policy_base_effects)
                        rprint(f"[bright_cyan]{advisor.name}[/]: {reply}")
                        thread.append(f"{advisor.name}: {reply}")
                        found = True
                        break  # Only ask the first matching advisor
                if not found:
                    rprint(f"[red]Advisor '{advisor_name}' not found.[/]")

            elif command.startswith("all "):
                msg = command[4:]
                thread.append(f"Player to all: {msg}")
                for advisor in council.advisors:
                    # Pass policy_base_effects_list to individual advisor queries too
                    reply = await advisor.advise(model, crisis_text, options, state.to_dict(), thread, current_turn_policy_base_effects)
                    if reply != "...":
                        rprint(f"[bright_cyan]{advisor.name}[/]: {reply}")
                        thread.append(f"{advisor.name}: {reply}")

            elif command.startswith("!choose"):
                parts = command.strip().split()
                if len(parts) != num_options + 1:
                    rprint(f"[red]Invalid format. Expected {num_options} allocation values after !choose.[/]")
                    rprint(f"[dim italic]Example: !choose {' '.join(['33'] * num_options)}[/dim italic]")
                    continue
                
                try:
                    alloc_values = [int(p) for p in parts[1:]]
                    if sum(alloc_values) != 100:
                        rprint(f"[red]Allocations must sum to 100. Current sum: {sum(alloc_values)}[/]")
                        continue
                    if any(a < 0 for a in alloc_values):
                        rprint(f"[red]Allocations cannot be negative.[/]")
                        continue
                    
                    chosen_allocations = [val / 100.0 for val in alloc_values]

                except ValueError:
                    rprint("[red]Invalid allocation values. Please enter numbers (percentages).[/]")
                    continue


            elif command.lower() == "log":
                rprint("\n\n".join(thread))

            elif command.lower() == "quit":
                rprint("Abdicating...")
                return

        deltas = apply_policy(chosen_allocations, state, current_turn_policy_base_effects)

        print_stats(state, deltas)

        council.update_influence()    
    
    rprint(Panel("Your reign has ended. Let’s see who gained the most power.", title="End of Game"))
    for name, persona, goal, influence in council.reveal_goals():
        rprint(f"[italic]{name} ({persona})[/]: [bold]Secret Goal[/] → {goal}, [bold]Influence[/]: {influence}")
        