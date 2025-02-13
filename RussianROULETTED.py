import random
import time

# -------- Card and Deck Classes --------

class Card:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Card({self.name})"

class Deck:
    def __init__(self):
        self.cards = []
        self.populate_deck()
        random.shuffle(self.cards)

    def populate_deck(self):
        # New card names and (equal) frequencies – exactly as provided.
        new_cards_config = {
            "Respin": 4,
            "Focused action": 4,
            "Domain Expansion: Casino": 4,
            "Peek’ n see": 4,
            "Gimme those": 4,
            "Nope": 4,
            "Just 1 more": 4,
            "Bullets!!!": 4,
            "Get that out of here": 4,
            "Another just for you": 4,
            "And you get a bullet and you get a bullet and you….": 4,
            "You owe me…": 4,
            "Can’t touch this": 4,
            "Reverse": 4,
            "Ambidextrous": 4,
            "Master of fate": 4,
            "No balls": 4,
            "Enhanced nope": 4,
            "Give Jimmy a chance": 4,
            "Whatcha u’ got of there": 4,
            "I think I’ll be take this": 4,
            "Let’s go gambling": 4,
            "Anotha’ time": 4
        }
        self.cards = []
        for card_name, count in new_cards_config.items():
            self.cards.extend([Card(card_name) for _ in range(count)])
        random.shuffle(self.cards)
    
    def draw(self, n):
        drawn = []
        for _ in range(n):
            if not self.cards:
                self.populate_deck()
                random.shuffle(self.cards)
            drawn.append(self.cards.pop())
        return drawn

# -------- Player Class --------

class Player:
    def __init__(self, name, deck):
        self.name = name
        # Start with 4 cards instead of 5.
        self.hand = deck.draw(4)
        # One-turn or multi-turn effects:
        self.safe_trigger = False       # For "Can’t touch this"
        self.extra_life_rounds = 0      # From "Focused action"
        self.pending_bullet_modifier = 0    # Delayed bullet modifications
        self.forced_extra_turn = False      # Force extra trigger pull
        self.extra_cards_next_round = 0     # Extra card plays next round
        self.block_active = False           # For "Enhanced nope"

    def discard_and_draw(self, indices, deck):
        indices = sorted(indices, reverse=True)
        for i in indices:
            if 0 <= i < len(self.hand):
                del self.hand[i]
        new_cards = deck.draw(len(indices))
        self.hand.extend(new_cards)
    
    def refill_hand(self, deck):
        # Ensure the hand always has exactly 4 cards.
        needed = 4 - len(self.hand)
        if needed > 0:
            self.hand.extend(deck.draw(needed))

    def show_hand(self):
        for idx, card in enumerate(self.hand):
            print(f"  {idx}: {card.name}")

# -------- Revolver Class --------

class Revolver:
    def __init__(self, num_chambers=6):
        self.num_chambers = num_chambers
        self.chambers = [False] * num_chambers
        # Load one bullet into a random chamber.
        bullet_index = random.randint(0, num_chambers - 1)
        self.chambers[bullet_index] = True
        # Set the starting chamber index at random.
        self.current_chamber = random.randint(0, num_chambers - 1)

    def spin(self):
        self.current_chamber = random.randint(0, self.num_chambers - 1)

    def pull_trigger(self):
        result = self.chambers[self.current_chamber]
        self.current_chamber = (self.current_chamber + 1) % self.num_chambers
        return result

    def add_bullet(self):
        empty_indices = [i for i, loaded in enumerate(self.chambers) if not loaded]
        if empty_indices:
            index = random.choice(empty_indices)
            self.chambers[index] = True
            return True
        return False

    def remove_bullet(self):
        loaded_indices = [i for i, loaded in enumerate(self.chambers) if loaded]
        if loaded_indices:
            index = random.choice(loaded_indices)
            self.chambers[index] = False
            return True
        return False

# -------- Game Class --------

class Game:
    def __init__(self, player_names):
        self.deck = Deck()
        self.players = [Player(name, self.deck) for name in player_names]
        self.revolver = Revolver()
        self.active_players = self.players[:]  # Players still in the game.
        self.current_player_index = 0
        self.last_card_played = None  # To support replication effects.

    def choose_target(self, current_player, prompt="Choose a target by index:"):
        # List all active players excluding current_player.
        valid_targets = [p for p in self.active_players if p != current_player]
        if not valid_targets:
            print("No valid targets.")
            return None
        print("Available targets:")
        for idx, p in enumerate(valid_targets):
            print(f"  {idx}: {p.name}")
        try:
            target_index = int(input(prompt))
            if 0 <= target_index < len(valid_targets):
                return valid_targets[target_index]
            else:
                print("Invalid index; no target selected.")
                return None
        except ValueError:
            print("Invalid input; no target selected.")
            return None

    def resolve_trigger(self, player):
        # This function handles the suspense and resolution of pulling the trigger.
        print("\nYou steady your nerves...")
        time.sleep(1.5)
        print("You slowly bring the gun to your head...")
        time.sleep(1.5)
        print("The sound of the mechanism echoes in the silence...")
        time.sleep(1.5)
        print("...")
        time.sleep(1)
        print(f"{player.name} pulls the trigger...")
        time.sleep(1)
        trigger_result = self.revolver.pull_trigger()
        time.sleep(1)

        if trigger_result:
            if player.safe_trigger:
                print("Bang! But your 'Can’t touch this' protects you!")
                player.safe_trigger = False
                return "survived"
            elif player.extra_life_rounds > 0:
                print("Bang! But your extra life from 'Focused action' saves you!")
                player.extra_life_rounds = 0
                return "survived"
            else:
                print("Bang! A bullet fires!")
                print(f"{player.name} has been eliminated!")
                return "eliminated"
        else:
            print("Click! The chamber was empty. You survived this round!")
            return "survived"

    def apply_card_effect(self, card, player):
        # For replication purposes, do not update the last played card if using "Anotha’ time".
        if card.name != "Anotha’ time":
            self.last_card_played = card

        if card.name == "Respin":
            self.revolver.spin()
            print("  -> The revolver has been respun!")
        elif card.name == "Focused action":
            choice = input("Do you want to (k)ill a chosen player immediately or gain extra life for 3 rounds? (k/e): ").strip().lower()
            if choice == 'k':
                target = self.choose_target(player, "Choose a target to eliminate: ")
                if target:
                    if target.block_active:
                        print(f"  -> {target.name} blocked the effect!")
                        target.block_active = False
                    else:
                        print(f"  -> {target.name} has been eliminated by your Focused action!")
                        self.active_players.remove(target)
                        if self.current_player_index >= len(self.active_players):
                            self.current_player_index = 0
            else:
                player.extra_life_rounds = 3
                print("  -> Focused action activated: You gain an extra life for the next 3 rounds!")
        elif card.name == "Domain Expansion: Casino":
            # If played twice in a row, force everyone to discard and redraw.
            if self.last_card_played and self.last_card_played.name == "Domain Expansion: Casino":
                for p in self.active_players:
                    num_cards = len(p.hand)
                    p.hand = self.deck.draw(num_cards)
                    print(f"  -> {p.name}'s hand has been discarded and redrawn!")
                print("  -> Domain Expansion: Casino activated twice in a row! Everyone's hand has been reshuffled!")
            else:
                print("  -> Domain Expansion: Casino played. Play it again consecutively to force a hand reshuffle!")
        elif card.name == "Peek’ n see":
            chamber = self.revolver.current_chamber
            status = "loaded" if self.revolver.chambers[chamber] else "empty"
            print(f"  -> You peek at the chamber: Chamber {chamber} is {status}.")
        elif card.name == "Gimme those":
            target = self.choose_target(player, "Choose a player to swap hands with: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the hand swap!")
                    target.block_active = False
                else:
                    player.hand, target.hand = target.hand, player.hand
                    print(f"  -> You swapped hands with {target.name}!")
        elif card.name == "Nope":
            print(f"  -> {player.name} has chosen to skip pulling the trigger this turn.")
            return "skip"
        elif card.name == "Just 1 more":
            if self.revolver.add_bullet():
                print("  -> A bullet has been added to the revolver!")
            else:
                print("  -> The revolver is full! No bullet was added.")
        elif card.name == "Bullets!!!":
            added = 0
            for _ in range(2):
                if self.revolver.add_bullet():
                    added += 1
            print(f"  -> {added} bullet(s) have been added to the revolver!")
        elif card.name == "Get that out of here":
            if self.revolver.remove_bullet():
                print("  -> A bullet has been removed from the revolver!")
            else:
                print("  -> There were no bullets to remove!")
        elif card.name == "Another just for you":
            target = self.choose_target(player, "Choose a target for +1 bullet next turn: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the effect!")
                    target.block_active = False
                else:
                    target.pending_bullet_modifier += 1
                    print(f"  -> {target.name}'s chamber will have +1 bullet added next turn!")
        elif card.name == "And you get a bullet and you get a bullet and you….": 
            target = self.choose_target(player, "Choose a target for +2 bullets next turn: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the effect!")
                    target.block_active = False
                else:
                    target.pending_bullet_modifier += 2
                    print(f"  -> {target.name}'s chamber will have +2 bullets added next turn!")
        elif card.name == "You owe me…":
            target = self.choose_target(player, "Choose a target for -1 bullet next turn: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the effect!")
                    target.block_active = False
                else:
                    target.pending_bullet_modifier -= 1
                    print(f"  -> {target.name}'s chamber will have 1 bullet removed next turn!")
        elif card.name == "Can’t touch this":
            player.safe_trigger = True
            print("  -> Can’t touch this activated! You will be immune to a bullet this turn.")
        elif card.name == "Reverse":
            self.active_players.reverse()
            self.current_player_index = self.active_players.index(player)
            print("  -> The order of play is reversed!")
        elif card.name == "Ambidextrous":
            player.extra_cards_next_round = 2
            print("  -> Ambidextrous activated: Next round, you may play 2 cards!")
        elif card.name == "Master of fate":
            try:
                choice = int(input(f"Enter a chamber index (0-{self.revolver.num_chambers - 1}) to set as next: "))
                if 0 <= choice < self.revolver.num_chambers:
                    self.revolver.current_chamber = choice
                    print(f"  -> The next chamber is now {choice}.")
                else:
                    print("  -> Invalid index. No changes made.")
            except ValueError:
                print("  -> Invalid input. No changes made.")
        elif card.name == "No balls":
            if len(self.active_players) > 1:
                next_index = (self.current_player_index + 1) % len(self.active_players)
                target = self.active_players[next_index]
                target.forced_extra_turn = True
                print(f"  -> {target.name} will be forced to pull the trigger again after their turn!")
        elif card.name == "Enhanced nope":
            player.block_active = True
            print("  -> Enhanced nope activated! Your next targeted card effect will be blocked.")
        elif card.name == "Give Jimmy a chance":
            target = self.choose_target(player, "Choose a player to force to fire: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the forced trigger effect!")
                    target.block_active = False
                else:
                    print(f"  -> {player.name} forces {target.name} to pull the trigger instead!")
                    result = self.resolve_trigger(target)
                    if result == "eliminated":
                        self.active_players.remove(target)
                        if self.current_player_index >= len(self.active_players):
                            self.current_player_index = 0
                    return "forced"
        elif card.name == "Whatcha u’ got of there":
            target = self.choose_target(player, "Choose a player to look at their hand: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the hand reveal!")
                    target.block_active = False
                else:
                    print(f"  -> {target.name}'s hand:")
                    for c in target.hand:
                        print(f"     - {c.name}")
        elif card.name == "I think I’ll be take this":
            target = self.choose_target(player, "Choose a player to steal a card from: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the steal!")
                    target.block_active = False
                else:
                    if target.hand:
                        stolen = random.choice(target.hand)
                        target.hand.remove(stolen)
                        player.hand.append(stolen)
                        print(f"  -> You stole a card from {target.name}!")
                    else:
                        print(f"  -> {target.name} has no cards to steal.")
        elif card.name == "Let’s go gambling":
            target = self.choose_target(player, "Choose a player to force a hand discard: ")
            if target:
                if target.block_active:
                    print(f"  -> {target.name} blocked the reshuffle!")
                    target.block_active = False
                else:
                    num_cards = len(target.hand)
                    target.hand = self.deck.draw(num_cards)
                    print(f"  -> {target.name}'s hand has been discarded and redrawn!")
        elif card.name == "Anotha’ time":
            if self.last_card_played and self.last_card_played.name != "Anotha’ time":
                print(f"  -> Replicating the effect of {self.last_card_played.name}!")
                self.apply_card_effect(self.last_card_played, player)
            else:
                print("  -> No valid last card to replicate.")
        return None

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.active_players)

    def play(self):
        print("=== Starting Russian Roulette with Cards! ===")
        round_count = 1
        while len(self.active_players) > 1:
            print("\n========================================")
            print(f"Round {round_count}")
            current_player = self.active_players[self.current_player_index]
            print(f"\nIt's {current_player.name}'s turn!")

            # --- Apply any pending bullet modifications to this player's turn ---
            if current_player.pending_bullet_modifier != 0:
                mod = current_player.pending_bullet_modifier
                if mod > 0:
                    for _ in range(mod):
                        self.revolver.add_bullet()
                    print(f"  -> {current_player.name}'s chamber was modified: +{mod} bullet(s) added!")
                elif mod < 0:
                    for _ in range(abs(mod)):
                        self.revolver.remove_bullet()
                    print(f"  -> {current_player.name}'s chamber was modified: {mod} bullet(s) removed!")
                current_player.pending_bullet_modifier = 0

            # --- Let the player play cards (normal play) ---
            print("Your current hand:")
            current_player.show_hand()
            action = input("Choose an action: (p)lay a card, (d)iscard to redraw, or (n)one: ").strip().lower()
            if action == 'p':
                try:
                    card_index = int(input("Enter the index of the card to play: "))
                    if 0 <= card_index < len(current_player.hand):
                        card = current_player.hand.pop(card_index)
                        print(f"  You play {card.name}.")
                        effect = self.apply_card_effect(card, current_player)
                        if effect in ("skip", "forced"):
                            current_player.refill_hand(self.deck)
                            self.next_player()
                            round_count += 1
                            continue
                    else:
                        print("  Invalid index; no card played.")
                except ValueError:
                    print("  Invalid input; no card played.")
            elif action == 'd':
                discard_str = input("Enter indices of cards to discard separated by spaces (or press Enter to cancel): ")
                if discard_str.strip():
                    try:
                        indices = list(map(int, discard_str.split()))
                        current_player.discard_and_draw(indices, self.deck)
                        print("Your new hand:")
                        current_player.show_hand()
                    except ValueError:
                        print("  Invalid input; no cards discarded.")
                action = input("Now, do you want to play a card? (p)lay or (n)one: ").strip().lower()
                if action == 'p':
                    try:
                        card_index = int(input("Enter the index of the card to play: "))
                        if 0 <= card_index < len(current_player.hand):
                            card = current_player.hand.pop(card_index)
                            print(f"  You play {card.name}.")
                            effect = self.apply_card_effect(card, current_player)
                            if effect in ("skip", "forced"):
                                current_player.refill_hand(self.deck)
                                self.next_player()
                                round_count += 1
                                continue
                        else:
                            print("  Invalid index; no card played.")
                    except ValueError:
                        print("  Invalid input; no card played.")
            else:
                print("  No card action taken.")

            # --- Allow extra card plays if the player earned them ---
            while current_player.extra_cards_next_round > 0:
                extra_action = input("You have an extra card play opportunity! (p)lay a card or (n)one: ").strip().lower()
                if extra_action == 'p':
                    try:
                        card_index = int(input("Enter the index of the card to play: "))
                        if 0 <= card_index < len(current_player.hand):
                            card = current_player.hand.pop(card_index)
                            print(f"  You play {card.name}.")
                            effect = self.apply_card_effect(card, current_player)
                            if effect in ("skip", "forced"):
                                # If an extra play forces a skip/forced, break out.
                                break
                        else:
                            print("  Invalid index; no card played.")
                    except ValueError:
                        print("  Invalid input; no card played.")
                else:
                    break
                current_player.extra_cards_next_round -= 1

            # --- Trigger Pull (Normal) ---
            result = self.resolve_trigger(current_player)
            if result == "eliminated":
                self.active_players.pop(self.current_player_index)
                if not self.active_players:
                    print("All players have been eliminated!")
                    break
                self.current_player_index %= len(self.active_players)
                # No need to refill hand for an eliminated player.
            elif current_player.forced_extra_turn:
                print(f"  -> {current_player.name} is forced to pull the trigger again!")
                current_player.forced_extra_turn = False
                result = self.resolve_trigger(current_player)
                if result == "eliminated":
                    self.active_players.pop(self.current_player_index)
                    if not self.active_players:
                        print("All players have been eliminated!")
                        break
                    self.current_player_index %= len(self.active_players)
                    round_count += 1
                    continue

            current_player.safe_trigger = False
            time.sleep(1)
            # Refill the player's hand so it always has 4 cards.
            current_player.refill_hand(self.deck)
            self.next_player()
            round_count += 1

        if self.active_players:
            print("\n=== Game Over! ===")
            print(f"{self.active_players[0].name} is the last person standing!")
        else:
            print("Game Over! No winners.")

# -------- Main Function --------

def main():
    print("Welcome to Russian Roulette with Cards!")
    try:
        player_count = int(input("Enter the number of players: "))
    except ValueError:
        print("Invalid number, exiting.")
        return
    player_names = []
    for i in range(player_count):
        name = input(f"Enter name for player {i+1}: ")
        player_names.append(name)
    game = Game(player_names)
    game.play()

if __name__ == "__main__":
    main()
