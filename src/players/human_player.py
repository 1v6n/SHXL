from src.players.abstract_player import Player


class HumanPlayer(Player):
    """Human player that interacts through the console"""

    def _display_players(self, players):
        """Display a list of players with their IDs"""
        print("\nAvailable players:")
        for player in players:
            print(f"  {player.name} - ID {player.id}")

    def _get_player_choice(self, players, action_name):
        """Get player choice from the console"""
        while True:
            try:
                self._display_players(players)
                choice = int(input(f"\nEnter player ID to {action_name}: "))
                player = next((p for p in players if p.id == choice), None)
                if player:
                    return player
                print("Invalid player ID. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def _display_role_info(self):
        """Display role information to the player"""
        print(f"\n{'-'*60}")
        print(f"You are {self.name}")
        print(f"Your role: {self.role}")

        # Show information about other players if available
        if self.is_fascist and not self.is_hitler:
            print("\nYou know the following information:")
            print(f"  Hitler is {self.hitler.name}")
            if self.fascists:
                print(
                    f"  Your fellow fascists are: {', '.join([f'{p.name}' for p in self.fascists if p.id != self.player_id])}"
                )

        if self.is_hitler and self.fascists:
            # Only in games with < 8 players
            print("\nYou know the following information:")
            print(
                f"  Your fellow fascists are: {', '.join([f'Player {p.id}: {p.name}' for p in self.fascists])}"
            )

        if self.is_communist and self.known_communists:
            print("\nYou know the following information:")
            print(
                f"  Your fellow communists are: {', '.join([f'Player {p}' for p in self.known_communists])}"
            )

        # Show inspected players
        if self.inspected_players:
            print("\nPlayers you have inspected:")
            for player_id, party in self.inspected_players.items():
                print(f"  Player {player_id} is a member of the {party} party")

        print(f"{'-'*60}\n")

    def nominate_chancellor(self, eligible_players=None):
        """
        Choose a chancellor interactively

        Returns:
            player: The nominated chancellor
        """
        print("\n=== CHANCELLOR NOMINATION ===")
        self._display_role_info()

        if eligible_players is None:
            eligible_players = self.state.get_eligible_chancellors()

        print("As President, you must nominate a Chancellor.")
        return self._get_player_choice(eligible_players, "nominate as Chancellor")

    def filter_policies(self, policies):
        """
        Choose which policies to pass as president

        Args:
            policies: List of 3 policies

        Returns:
            tuple: (chosen [2], discarded [1])
        """
        print("\n=== PRESIDENTIAL POLICY SELECTION ===")
        self._display_role_info()

        print("As President, you must select 2 policies to pass to the Chancellor.")
        print("Policies drawn:")
        for i, policy in enumerate(policies):
            print(f"  {i+1}. {policy.type}")

        while True:
            try:
                discard_idx = (
                    int(input("\nEnter the number of the policy to DISCARD (1-3): "))
                    - 1
                )
                if 0 <= discard_idx < len(policies):
                    discarded = policies[discard_idx]
                    chosen = [p for p in policies if p != discarded]
                    print(f"You discarded: {discarded.type}")
                    return chosen, discarded
                print("Invalid policy number. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def choose_policy(self, policies):
        """
        Choose which policy to enact as chancellor

        Args:
            policies: List of 2 policies

        Returns:
            tuple: (chosen [1], discarded [1])
        """
        print("\n=== CHANCELLOR POLICY SELECTION ===")
        self._display_role_info()

        print("As Chancellor, you must select 1 policy to enact.")
        print("Policies received from President:")
        for i, policy in enumerate(policies):
            print(f"  {i+1}. {policy.type}")

        while True:
            try:
                enact_idx = (
                    int(input("\nEnter the number of the policy to ENACT (1-2): ")) - 1
                )
                if 0 <= enact_idx < len(policies):
                    chosen = policies[enact_idx]
                    discarded = [p for p in policies if p != chosen][0]
                    print(f"You enacted: {chosen.type}")
                    return chosen, discarded
                print("Invalid policy number. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def vote(self):
        """
        Vote on a government

        Returns:
            bool: True for Ja, False for Nein
        """
        print("\n=== GOVERNMENT VOTE ===")
        self._display_role_info()

        print(
            f"Proposed government: President = {self.state.president_candidate.name}, Chancellor = Player {self.state.chancellor_candidate.name}"
        )

        while True:
            vote = input("Vote (ja/nein): ").lower().strip()
            if vote in ["ja", "j", "yes", "y"]:
                return True
            elif vote in ["nein", "n", "no"]:
                return False
            print("Invalid vote. Please enter 'ja' or 'nein'.")

    def veto(self):
        """
        Decide whether to veto (as chancellor)

        Returns:
            bool: True to veto, False otherwise
        """
        if not self.state.board.veto_available:
            return False

        print("\n=== VETO OPTION ===")
        self._display_role_info()

        print("As Chancellor, you can propose a veto.")
        print("Current policies:")
        for i, policy in enumerate(self.state.current_policies):
            print(f"  {i+1}. {policy.type}")

        while True:
            veto = (
                input("Do you want to veto these policies? (yes/no): ").lower().strip()
            )
            if veto in ["yes", "y"]:
                return True
            elif veto in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def accept_veto(self):
        """
        Decide whether to accept veto (as president)

        Returns:
            bool: True to accept veto, False otherwise
        """
        print("\n=== VETO CONFIRMATION ===")
        self._display_role_info()

        print("As President, the Chancellor has proposed a veto.")
        print("Current policies:")
        for i, policy in enumerate(self.state.current_policies):
            print(f"  {i+1}. {policy.type}")

        while True:
            accept = input("Do you accept the veto? (yes/no): ").lower().strip()
            if accept in ["yes", "y"]:
                return True
            elif accept in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def view_policies(self, policies):
        """
        React to seeing policies with Policy Peek

        Args:
            policies: List of policies
        """
        print("\n=== POLICY PEEK ===")
        self._display_role_info()
        print("You see the following policies on top of the deck:")
        for i, policy in enumerate(policies):
            print(f"  {i+1}. {policy.type}")
        input("Press Enter to continue...")

    def kill(self):
        """
        Choose a player to execute immediately

        Returns:
            player: The chosen player
        """
        print("\n=== IMMEDIATE EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to execute.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "execute")

    def choose_player_to_mark(self):
        """
        Choose a player to mark for execution
        Returns:
            player: The chosen player
        """
        print("\n=== MARK FOR EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to mark for execution.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "mark for execution")

    def inspect_player(self):
        """
        Choose a player to inspect

        Returns:
            player: The chosen player
        """
        print("\n=== LOYALTY INSPECTION ===")
        self._display_role_info()

        print("As President, you must choose a player to investigate.")

        uninspected = [
            p
            for p in self.state.active_players
            if p != self and p.id not in self.inspected_players
        ]

        # If all players have been inspected, can inspect any player
        eligible_players = (
            uninspected
            if uninspected
            else [p for p in self.state.active_players if p != self]
        )

        return self._get_player_choice(eligible_players, "inspect")

    def choose_next(self):
        """
        Choose the next president (special election)

        Returns:
            player: The chosen player
        """
        print("\n=== SPECIAL ELECTION ===")
        self._display_role_info()

        print("As President, you must choose the next presidential candidate.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "nominate as next President")

    def choose_player_to_radicalize(self):
        """
        Choose a player to convert to communist

        Returns:
            player: The chosen player
        """
        print("\n=== RADICALIZATION ===")
        self._display_role_info()

        print("As President, you must choose a player to convert to Communist.")
        # Cannot radicalize Hitler or self
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "radicalize")

    def propaganda_decision(self, policy):
        """
        Decide whether to discard the top policy

        Args:
            policy: The top policy

        Returns:
            bool: True to discard, False to keep
        """
        print("\n=== PROPAGANDA ===")
        self._display_role_info()

        print(f"The top policy card is: {policy.type}")

        while True:
            decision = (
                input("Do you want to discard this policy? (yes/no): ").lower().strip()
            )
            if decision in ["yes", "y"]:
                return True
            elif decision in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def choose_revealer(self, eligible_players):
        """
        Choose a player to reveal party membership to (Impeachment)

        Returns:
            player: The chosen player
        """
        print("\n=== IMPEACHMENT ===")
        self._display_role_info()

        print(
            "As President, you must choose a player to reveal the Chancellor's party membership to."
        )
        return self._get_player_choice(eligible_players, "reveal party membership to")

    def social_democratic_removal_choice(self, state):
        """
        Choose which policy track to remove from (Social Democratic)

        Returns:
            str: "fascist" or "communist"
        """
        print("\n=== SOCIAL DEMOCRATIC ===")
        self._display_role_info()

        print("You must choose which policy track to remove a policy from.")

        while True:
            track = input("Choose a track (fascist/communist): ").lower().strip()
            if track in ["fascist", "f"]:
                return "fascist"
            elif track in ["communist", "c"]:
                return "communist"
            print("Invalid track. Please enter 'fascist' or 'communist'.")

    def mark_for_execution(self):
        """
        Choose a player to mark for execution

        Returns:
            player: The chosen player
        """
        print("\n=== MARK FOR EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to mark for execution.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "mark for execution")

    def choose_player_to_bug(self):
        """
        Choose a player to bug (view party membership)

        Returns:
            player: The chosen player
        """
        print("\n=== BUGGING ===")
        self._display_role_info()

        print("As President, you must choose a player to bug.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "bug")

    def pardon_player(self):
        """
        Choose to pardon the player marked for execution

        Returns:
            bool: True to pardon, False otherwise
        """
        print("\n=== PRESIDENTIAL PARDON ===")
        self._display_role_info()

        marked_player = self.state.marked_for_execution
        print(
            f"Player {marked_player.id}: {marked_player.name} is currently marked for execution."
        )

        while True:
            pardon = (
                input("Do you want to pardon this player? (yes/no): ").lower().strip()
            )
            if pardon in ["yes", "y"]:
                return True
            elif pardon in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def chancellor_veto_proposal(self, policies):
        """
        As Chancellor, decide whether to propose a veto when veto power is available

        Args:
            policies: List of 2 policies

        Returns:
            bool: True to propose veto, False to enact a policy
        """
        # If veto is not available, don't offer the option
        if not self.state.veto_available:
            return False

        print("\n=== VETO OPTION (CHANCELLOR) ===")
        self._display_role_info()

        print("As Chancellor, you can propose a veto of these policies.")
        print("Policies received from President:")
        for i, policy in enumerate(policies):
            print(f"  {i+1}. {policy.type}")

        while True:
            decision = (
                input("Do you want to propose a veto? (yes/no): ").lower().strip()
            )
            if decision in ["yes", "y"]:
                return True
            elif decision in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def vote_of_no_confidence(self):
        """
        As Chancellor with Enabling Act power, decide whether to enact the discarded policy

        Returns:
            bool: True to enact the discarded policy, False to leave it
        """
        print("\n=== VOTE OF NO CONFIDENCE ===")
        self._display_role_info()

        if self.state.last_discarded:
            print(f"The last discarded policy is: {self.state.last_discarded.type}")

            while True:
                decision = (
                    input("Do you want to enact this policy? (yes/no): ")
                    .lower()
                    .strip()
                )
                if decision in ["yes", "y"]:
                    return True
                elif decision in ["no", "n"]:
                    return False
                print("Invalid choice. Please enter 'yes' or 'no'.")
        else:
            print("No policy was discarded in this legislative phase.")
            return False

    def chancellor_propose_veto(self, policies):
        """
        Chancellor proposes a veto when veto power is available

        Args:
            policies: List of 2 policies the Chancellor received

        Returns:
            bool: True to propose a veto, False otherwise
        """
        # Only offer veto if it's available
        if not self.state.veto_available:
            return False

        print("\n=== CHANCELLOR VETO OPTION ===")
        self._display_role_info()

        print("As Chancellor, you can propose a veto.")
        print("Policies received from President:")
        for i, policy in enumerate(policies):
            print(f"  {i+1}. {policy.type}")

        while True:
            veto = input("Do you want to propose a veto? (yes/no): ").lower().strip()
            if veto in ["yes", "y"]:
                return True
            elif veto in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def choose_player_to_mark_for_execution(self):
        """
        Choose a player to mark for future execution

        Returns:
            player: The player to mark
        """
        print("\n=== MARK FOR EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to mark for execution.")
        print("They will be executed after 3 fascist policies are enacted.")

        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "mark for execution")

    def choose_to_pardon(self):
        """
        Choose whether to pardon the player marked for execution

        Returns:
            bool: True to pardon, False otherwise
        """
        print("\n=== PARDON ===")
        self._display_role_info()

        marked_player = self.state.marked_for_execution

        if not marked_player:
            print("No player is marked for execution.")
            return False

        print(
            f"Player {marked_player.id}: {marked_player.name} is currently marked for execution."
        )

        while True:
            pardon = (
                input("Do you want to pardon this player? (yes/no): ").lower().strip()
            )
            if pardon in ["yes", "y"]:
                return True
            elif pardon in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def no_confidence_decision(self):
        """
        Decide whether to enact the discarded policy (Vote of No Confidence)

        Returns:
            bool: True to enact, False otherwise
        """
        print("\n=== VOTE OF NO CONFIDENCE ===")
        self._display_role_info()

        if not self.state.last_discarded:
            print("No policy was discarded in this legislative phase.")
            return False

        print(
            f"The last policy discarded by the President is: {self.state.last_discarded.type}"
        )

        while True:
            enact = (
                input("Do you want to enact this policy? (yes/no): ").lower().strip()
            )
            if enact in ["yes", "y"]:
                return True
            elif enact in ["no", "n"]:
                return False
            print("Invalid choice. Please enter 'yes' or 'no'.")

    def choose_player_to_investigate(self, eligible_players):
        """
        Choose a player to investigate their party membership

        Args:
            eligible_players: List of players that can be investigated

        Returns:
            player: The player to investigate
        """
        print("\n=== INVESTIGATE LOYALTY ===")
        self._display_role_info()

        print("As President, you can investigate a player's party membership.")
        return self._get_player_choice(eligible_players, "investigate")

    def choose_next_president(self, eligible_players):
        """
        Choose the next president for a special election

        Args:
            eligible_players: List of players that can be chosen as next president

        Returns:
            player: The player to be the next president
        """
        print("\n=== SPECIAL ELECTION ===")
        self._display_role_info()

        print("As President, you can choose the next president for a special election.")
        return self._get_player_choice(eligible_players, "choose as next president")
