"""Jugador humano para Secret Hitler XL.

Este módulo define la clase HumanPlayer que representa un jugador controlado
por un humano a través de la consola, con interfaces interactivas para
todas las decisiones del juego.
"""

from src.players.abstract_player import Player


class HumanPlayer(Player):
    """Jugador controlado por humano que interactúa a través de la consola.

    Extiende la clase Player para proporcionar interfaces interactivas
    que permiten a los usuarios humanos tomar decisiones durante el juego.
    """

    def _display_players(self, players):
        """Muestra una lista de jugadores con sus IDs.

        Args:
            players (list): Lista de jugadores a mostrar.
        """
        print("\nAvailable players:")
        for player in players:
            print(f"  {player.name} - ID {player.id}")

    def _get_player_choice(self, players, action_name):
        """Obtiene la elección del jugador desde la consola.

        Args:
            players (list): Lista de jugadores disponibles.
            action_name (str): Nombre de la acción a realizar.

        Returns:
            Player: El jugador seleccionado.
        """
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
        """Muestra información del rol al jugador."""
        print(f"\n{'-'*60}")
        print(f"You are {self.name}")
        print(f"Your role: {self.role}")

        if self.is_fascist and not self.is_hitler:
            print("\nYou know the following information:")
            print(f"  Hitler is {self.hitler.name}")
            if self.fascists:
                print(
                    f"  Your fellow fascists are: {', '.join([f'{p.name}' for p in self.fascists if p.id != self.id])}"
                )

        if self.is_hitler and self.fascists:
            print("\nYou know the following information:")
            print(
                f"  Your fellow fascists are: {', '.join([f'Player {p.id}: {p.name}' for p in self.fascists])}"
            )

        if self.is_communist and self.known_communists:
            print("\nYou know the following information:")
            print(
                f"  Your fellow communists are: {', '.join([f'Player {p}' for p in self.known_communists])}"
            )

        if self.inspected_players:
            print("\nPlayers you have inspected:")
            for player_id, party in self.inspected_players.items():
                print(f"  Player {player_id} is a member of the {party} party")

        print(f"{'-'*60}\n")

    def nominate_chancellor(self, eligible_players=None):
        """Elige un canciller de forma interactiva.

        Args:
            eligible_players (list, optional): Jugadores elegibles como canciller.

        Returns:
            Player: El canciller nominado.
        """
        print("\n=== CHANCELLOR NOMINATION ===")
        self._display_role_info()

        if eligible_players is None:
            eligible_players = self.state.get_eligible_chancellors()

        print("As President, you must nominate a Chancellor.")
        return self._get_player_choice(eligible_players, "nominate as Chancellor")

    def filter_policies(self, policies):
        """Elige qué políticas pasar como presidente.

        Args:
            policies (list): Lista de 3 políticas.

        Returns:
            tuple: (políticas elegidas [2], política descartada [1]).
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
        """Elige qué política promulgar como canciller.

        Args:
            policies (list): Lista de 2 políticas.

        Returns:
            tuple: (política elegida [1], política descartada [1]).
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
        """Vota sobre un gobierno.

        Returns:
            bool: True para Ja, False para Nein.
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
        """Decide si vetar como canciller.

        Returns:
            bool: True para vetar, False en caso contrario.
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
        """Decide si aceptar el veto como presidente.

        Returns:
            bool: True para aceptar el veto, False en caso contrario.
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
        """Reacciona a ver políticas con espionaje de políticas.

        Args:
            policies (list): Lista de políticas vistas.
        """
        print("\n=== POLICY PEEK ===")
        self._display_role_info()
        print("You see the following policies on top of the deck:")
        for i, policy in enumerate(policies):
            print(f"  {i+1}. {policy.type}")
        input("Press Enter to continue...")

    def kill(self):
        """Elige un jugador para ejecutar inmediatamente.

        Returns:
            Player: El jugador elegido para ejecutar.
        """
        print("\n=== IMMEDIATE EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to execute.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "execute")

    def choose_player_to_mark(self):
        """Elige un jugador para marcar para ejecución.

        Returns:
            Player: El jugador elegido para marcar.
        """
        print("\n=== MARK FOR EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to mark for execution.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "mark for execution")

    def inspect_player(self):
        """Elige un jugador para inspeccionar.

        Returns:
            Player: El jugador elegido para inspeccionar.
        """
        print("\n=== LOYALTY INSPECTION ===")
        self._display_role_info()

        print("As President, you must choose a player to investigate.")

        uninspected = [
            p
            for p in self.state.active_players
            if p != self and p.id not in self.inspected_players
        ]

        eligible_players = (
            uninspected
            if uninspected
            else [p for p in self.state.active_players if p != self]
        )

        return self._get_player_choice(eligible_players, "inspect")

    def choose_next(self):
        """Elige el próximo presidente en elección especial.

        Returns:
            Player: El jugador elegido como próximo presidente.
        """
        print("\n=== SPECIAL ELECTION ===")
        self._display_role_info()

        print("As President, you must choose the next presidential candidate.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "nominate as next President")

    def choose_player_to_radicalize(self):
        """Elige un jugador para convertir al comunismo.

        Returns:
            Player: El jugador elegido para radicalizar.
        """
        print("\n=== RADICALIZATION ===")
        self._display_role_info()

        print("As President, you must choose a player to convert to Communist.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "radicalize")

    def propaganda_decision(self, policy):
        """Decide si descartar la política superior.

        Args:
            policy: La política superior del mazo.

        Returns:
            bool: True para descartar, False para mantener.
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
        """Elige un jugador para revelar afiliación política (Impeachment).

        Args:
            eligible_players (list): Jugadores elegibles.

        Returns:
            Player: El jugador elegido para revelar afiliación.
        """
        print("\n=== IMPEACHMENT ===")
        self._display_role_info()

        print(
            "As President, you must choose a player to reveal the Chancellor's party membership to."
        )
        return self._get_player_choice(eligible_players, "reveal party membership to")

    def social_democratic_removal_choice(self, state):
        """Elige qué pista de políticas eliminar (Socialdemócrata).

        Args:
            state: Estado actual del juego.

        Returns:
            str: "fascist" o "communist".
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
        """Elige un jugador para marcar para ejecución.

        Returns:
            Player: El jugador elegido para marcar.
        """
        print("\n=== MARK FOR EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to mark for execution.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "mark for execution")

    def choose_player_to_bug(self):
        """Elige un jugador para espiar su afiliación política.

        Returns:
            Player: El jugador elegido para espiar.
        """
        print("\n=== BUGGING ===")
        self._display_role_info()

        print("As President, you must choose a player to bug.")
        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "bug")

    def pardon_player(self):
        """Elige perdonar al jugador marcado para ejecución.

        Returns:
            bool: True para perdonar, False en caso contrario.
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
        """Como canciller, decide si proponer un veto cuando está disponible.

        Args:
            policies (list): Lista de 2 políticas.

        Returns:
            bool: True para proponer veto, False para promulgar política.
        """
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
        """Como canciller con poder de Ley Habilitante, decide si promulgar la política descartada.

        Returns:
            bool: True para promulgar política descartada, False para dejarla.
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
        """El canciller propone un veto cuando está disponible.

        Args:
            policies (list): Lista de 2 políticas que recibió el canciller.

        Returns:
            bool: True para proponer veto, False en caso contrario.
        """
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
        """Elige un jugador para marcar para ejecución futura.

        Returns:
            Player: El jugador a marcar.
        """
        print("\n=== MARK FOR EXECUTION ===")
        self._display_role_info()

        print("You must choose a player to mark for execution.")
        print("They will be executed after 3 fascist policies are enacted.")

        eligible_players = [p for p in self.state.active_players if p != self]
        return self._get_player_choice(eligible_players, "mark for execution")

    def choose_to_pardon(self):
        """Elige si perdonar al jugador marcado para ejecución.            bool: True para perdonar, False en caso contrario."""
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
        """Decide si promulgar la política descartada (Voto de No Confianza).

        Returns:
            bool: True para promulgar, False en caso contrario.
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
        """Elige un jugador para investigar su afiliación política.

        Args:
            eligible_players (list): Jugadores que pueden ser investigados.

        Returns:
            Player: El jugador a investigar.
        """
        print("\n=== INVESTIGATE LOYALTY ===")
        self._display_role_info()

        print("As President, you can investigate a player's party membership.")
        return self._get_player_choice(eligible_players, "investigate")

    def choose_next_president(self, eligible_players):
        """Elige el próximo presidente para elección especial.

        Args:
            eligible_players (list): Jugadores que pueden ser elegidos como próximo presidente.

        Returns:
            Player: El jugador que será el próximo presidente.
        """
        print("\n=== SPECIAL ELECTION ===")
        self._display_role_info()

        print("As President, you can choose the next president for a special election.")
        return self._get_player_choice(eligible_players, "choose as next president")
