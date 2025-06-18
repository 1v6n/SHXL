# Diagrama de Secuencia Completo - Secret Hitler XL (SHXL)

```mermaid
sequenceDiagram
    participant U as Usuario/Main
    participant G as SHXLGame
    participant S as EnhancedGameState
    participant B as GameBoard
    participant PF as PlayerFactory
    participant RF as RoleFactory
    participant PLF as PolicyFactory
    participant L as GameLogger
    participant SP as SetupPhase
    participant EP as ElectionPhase
    participant LP as LegislativePhase
    participant GP as GameOverPhase
    participant P as Player
    participant ST as PlayerStrategy
    participant POW as Power
    participant PR as PowerRegistry

    %% ===========================================
    %% INICIALIZACIÓN DEL JUEGO
    %% ===========================================

    Note over U,PR: 🎮 INICIALIZACIÓN DEL JUEGO

    U->>+G: SHXLGame(logger)
    G->>+S: EnhancedGameState()
    S-->>-G: state
    G->>+L: GameLogger(level)
    L-->>-G: logger
    G-->>-U: game

    U->>+G: setup_game(player_count, with_communists, with_anti_policies, ...)

    %% Crear tablero
    G->>+B: GameBoard(state, player_count, with_communists, logger)
    B->>B: _setup_fascist_powers()
    B->>B: _setup_communist_powers()
    B-->>-G: board
    G->>S: state.board = board

    %% Inicializar mazo de políticas
    G->>+PLF: PolicyFactory.create_policy_deck(...)
    PLF->>PLF: create policies based on configuration
    PLF-->>-G: policies
    G->>B: board.initialize_policy_deck(policy_factory, ...)
    B->>B: shuffle policies

    %% Crear jugadores
    G->>+PF: PlayerFactory()
    PF-->>-G: player_factory
    G->>PF: create_players(count, state, strategy_type, human_indices)

    loop for each player
        PF->>+P: AIPlayer/HumanPlayer(id, name, role, state, strategy)
        P->>+ST: PlayerStrategy(player)
        ST-->>-P: strategy
        P-->>-PF: player
        PF->>S: state.add_player(player)
    end

    %% Asignar roles
    G->>+RF: RoleFactory.create_roles(player_count, with_communists)
    RF->>RF: calculate role distribution
    RF->>RF: create and shuffle roles
    RF-->>-G: roles

    loop assign roles to players
        G->>P: player.role = role
        G->>P: player.initialize_role_attributes()
    end

    %% Informar jugadores sobre roles
    G->>G: inform_players()
    G->>G: _inform_fascists()
    G->>G: _inform_communists()

    %% Elegir primer presidente
    G->>G: choose_first_president()
    G->>S: state.president_candidate = random_player

    %% Verificar Oktober Fest
    alt month_counter == 10
        G->>S: state._start_oktoberfest()
        S->>S: save original strategies
        S->>P: switch all bots to RandomStrategy
    end

    %% Entrar en fase de setup
    G->>+SP: SetupPhase(self)
    SP-->>-G: setup_phase
    G->>G: current_phase = setup_phase

    G-->>-U: game configured

    %% ===========================================
    %% INICIO DEL JUEGO (BUCLE PRINCIPAL)
    %% ===========================================

    Note over U,PR: 🚀 INICIO DEL JUEGO

    U->>+G: start_game()

    loop while not game_over
        Note over G,GP: 🔄 BUCLE DE FASES
        G->>G: current_phase = current_phase.execute()

        alt current_phase is SetupPhase
            %% ===========================================
            %% FASE DE SETUP
            %% ===========================================
            Note over SP,EP: 🛠️ FASE DE SETUP
            G->>+SP: execute()
            SP->>+EP: ElectionPhase(game)
            EP-->>-SP: election_phase
            SP-->>-G: election_phase

        else current_phase is ElectionPhase
            %% ===========================================
            %% FASE DE ELECCIÓN
            %% ===========================================
            Note over EP,P: 🗳️ FASE DE ELECCIÓN
            G->>+EP: execute()

            %% Verificar jugadores marcados para ejecución
            EP->>EP: _check_marked_for_execution()
            alt player marked and 3+ fascist policies since marking
                EP->>P: target_player.is_dead = True
                EP->>S: state.active_players.remove(target_player)
                alt target_player.is_hitler
                    EP->>S: state.winner = "liberal" or "liberal_and_communist"
                    EP->>+GP: GameOverPhase(game)
                    GP-->>-EP: gameover_phase
                end
            end

            %% Nominación del canciller
            EP->>G: nominate_chancellor()
            G->>S: get_eligible_chancellors()
            S-->>G: eligible_players
              alt no eligible chancellors
                G->>G: enact_chaos_policy()
                G->>B: draw_policy(1)
                B-->>G: policy
                G->>B: enact_policy(policy, is_chaos=True)
                G->>S: state.election_tracker = 0
                alt check_policy_win()
                    G->>+GP: GameOverPhase(game)
                    GP-->>-G: gameover_phase
                    EP-->>-G: gameover_phase
                else
                    G->>S: state.term_limited_players = []
                    %% No deactivation here, EP stays active
                end
            else
                G->>P: president_candidate.nominate_chancellor(eligible_players)
                P->>ST: strategy.nominate_chancellor(eligible_players)
                ST-->>P: chosen_chancellor
                P-->>G: chosen_chancellor
                G->>S: state.chancellor_candidate = chosen_chancellor

                %% Votación del gobierno
                EP->>G: vote_on_government()

                loop for each active player
                    G->>P: player.vote()
                    P->>ST: strategy.vote(president, chancellor)
                    ST-->>P: vote_decision
                    P-->>G: vote (True/False)
                end

                G->>S: state.last_votes = votes
                G->>G: calculate vote result (majority wins)
                  alt vote passed
                    %% Verificar victoria fascista (Hitler como canciller)
                    alt fascist_track >= 3 and chancellor.is_hitler
                        G->>S: state.winner = "fascist"
                        G->>+GP: GameOverPhase(game)
                        GP-->>-G: gameover_phase
                    else
                        %% Gobierno elegido exitosamente
                        G->>S: state.president = president_candidate
                        G->>S: state.chancellor = chancellor_candidate
                        G->>S: state.election_tracker = 0
                        G->>+LP: LegislativePhase(game)
                        LP-->>-G: legislative_phase
                    end
                else vote failed
                    %% Votación fallida
                    G->>S: state.president = president_candidate
                    G->>S: state.election_tracker += 1

                    alt election_tracker >= 3
                        %% Tercera elección fallida - Caos
                        G->>L: log("Three failed elections - chaos policy")
                        G->>G: enact_chaos_policy()
                        G->>B: draw_policy(1)
                        B-->>G: policy
                        G->>B: enact_policy(policy, is_chaos=True)
                        G->>S: state.election_tracker = 0

                        alt check_policy_win()
                            G->>+GP: GameOverPhase(game)
                            GP-->>-G: gameover_phase
                        else
                            G->>S: state.term_limited_players = []
                        end
                    end

                    G->>G: set_next_president()
                    G->>S: advance_month_counter()

                    alt month_counter == 10 (Oktober Fest starts)
                        G->>S: state._start_oktoberfest()
                    else month_counter == 11 and oktoberfest_active
                        G->>S: state._end_oktoberfest()
                    end
                    %% No deactivation here, EP stays active
                end
            end

        else current_phase is LegislativePhase
            %% ===========================================
            %% FASE LEGISLATIVA
            %% ===========================================
            Note over LP,B: 📜 FASE LEGISLATIVA
            G->>+LP: execute()

            %% Presidente recibe 3 políticas
            LP->>G: state.board.draw_policy(3)
            G->>B: draw_policy(3)

            alt insufficient policies in deck
                B->>B: policies.extend(discards)
                B->>B: shuffle(policies)
                B->>L: log_shuffle(policies)
            end

            B-->>G: [policy1, policy2, policy3]
            G-->>LP: policies

            %% Presidente elige 2 políticas
            LP->>G: presidential_policy_choice(policies)
            G->>P: president.filter_policies(policies)
            P->>ST: strategy.filter_policies(policies)
            ST-->>P: (chosen_2_policies, discarded_1)
            P-->>G: (chosen, discarded)
            G-->>LP: (chosen, discarded)

            LP->>G: state.board.discard(discarded)
            G->>B: discard(discarded_policy)

            %% Canciller propone veto (si disponible)
            LP->>G: chancellor_propose_veto()

            alt veto_available (5+ fascist policies)
                G->>P: chancellor.veto()
                P->>ST: strategy.veto(policies)
                ST-->>P: veto_decision
                P-->>G: veto_decision

                alt chancellor proposes veto
                    LP->>G: president_veto_accepted()
                    G->>P: president.accept_veto()
                    P->>ST: strategy.accept_veto(policies)
                    ST-->>P: accept_decision
                    P-->>G: accept_decision
                      alt president accepts veto
                        LP->>G: state.board.discard(chosen)
                        LP->>G: state.election_tracker += 1
                        LP->>EP: ElectionPhase(game)
                        G->>G: current_phase = EP
                    end
                end
            end

            %% Canciller elige política final
            LP->>G: chancellor_policy_choice(chosen)
            G->>P: chancellor.choose_policy(chosen)
            P->>ST: strategy.choose_policy(policies)
            ST-->>P: (enacted_policy, discarded_policy)
            P-->>G: (enacted, discarded)
            G-->>LP: (enacted, discarded)

            LP->>G: state.board.discard(discarded)
            G->>B: discard(discarded_policy)

            %% Promulgar política
            LP->>G: state.board.enact_policy(enacted, False, emergency_powers, anti_policies)
            G->>B: enact_policy(enacted, ...)

            alt policy is anti-policy
                B->>B: _handle_anti_policy(policy)
                alt SocialDemocratic policy
                    B->>P: player.social_democratic_removal_choice(state)
                    P->>ST: strategy.social_democratic_removal_choice()
                    ST-->>P: "fascist" or "communist"
                    P-->>B: choice
                    alt choice == "fascist"
                        B->>B: fascist_track -= 1
                    else choice == "communist"
                        B->>B: communist_track -= 1
                    end
                end
            else policy is emergency policy
                B->>B: _handle_emergency_policy(policy)
            else normal policy
                alt policy.type == "liberal"
                    B->>B: liberal_track += 1
                else policy.type == "fascist"
                    B->>B: fascist_track += 1
                else policy.type == "communist"
                    B->>B: communist_track += 1
                end
            end

            %% Verificar poder otorgado
            B->>B: get_fascist_power() or get_communist_power()
            B-->>G: power_name or None
            G-->>LP: power_granted

            LP->>G: state.election_tracker = 0
            LP->>G: state.term_limited_players = []

            %% Establecer límites de término
            alt active_players > 7
                LP->>G: term_limited_players.append(last_president)
                alt last_chancellor != last_president
                    LP->>G: term_limited_players.append(last_chancellor)
                end
            else
                LP->>G: term_limited_players.append(last_chancellor)
            end

            %% Verificar condiciones de victoria
            LP->>G: check_policy_win()
            G->>B: check_win_condition()
            B-->>G: winner or None

            alt game won by policies
                G->>S: state.winner = winner
                G->>S: state.game_over = True
                LP->>GP: GameOverPhase(game)
                G->>G: current_phase = GP
            else
                %% Ejecutar poder si se otorgó
                alt power_granted
                    LP->>G: execute_power(power_name)
                    G->>+PR: PowerRegistry.get_power(power_name, game)
                    PR->>POW: Power(game)
                    POW-->>PR: power_instance
                    PR-->>-G: power_instance

                    alt power is presidential
                        G->>G: execute_presidential_power(power_name)

                        alt power_name == "investigate_loyalty"
                            G->>P: president.inspect_player()
                            P->>ST: strategy.choose_player_to_inspect(eligible)
                            ST-->>P: target_player
                            P-->>G: target_player
                            G->>POW: power.execute(target_player)
                            POW->>S: state.investigated_players.append(target)
                            POW-->>G: target_player.party_membership

                        else power_name == "special_election"
                            G->>P: president.choose_next()
                            P->>ST: strategy.choose_next_president(eligible)
                            ST-->>P: next_president
                            P-->>G: next_president
                            G->>POW: power.execute(next_president)
                            POW->>S: state.special_election = True
                            POW->>S: state.president_candidate = next_president
                            POW-->>G: next_president

                        else power_name == "policy_peek"
                            G->>POW: power.execute()
                            POW->>B: policies[:3]
                            B-->>POW: top_3_policies
                            POW-->>G: top_3_policies
                            G->>P: president.view_policies(policies)

                        else power_name == "execution"
                            G->>P: president.kill()
                            P->>ST: strategy.choose_player_to_kill(eligible)
                            ST-->>P: target_player
                            P-->>G: target_player
                            G->>POW: power.execute(target_player)
                            POW->>P: target_player.is_dead = True
                            POW->>S: state.active_players.remove(target_player)
                            POW-->>G: target_player

                            alt target_player.is_hitler
                                G->>S: state.game_over = True
                                alt communists_in_play
                                    G->>S: state.winner = "liberal_and_communist"
                                else
                                    G->>S: state.winner = "liberal"
                                end
                                LP->>+GP: GameOverPhase(game)
                                GP-->>-LP: gameover_phase
                                LP-->>-G: gameover_phase
                            end
                        end

                    else power is communist
                        G->>G: execute_communist_power(power_name)

                        alt power_name == "confession"
                            G->>POW: power.execute()
                            POW->>S: state.revealed_affiliations[president.id] = president.party
                            POW-->>G: president.party_membership

                        else power_name == "bugging"
                            G->>P: president.choose_player_to_bug()
                            P->>ST: strategy.choose_player_to_bug(eligible)
                            ST-->>P: target_player
                            P-->>G: target_player
                            G->>POW: power.execute(target_player)

                            loop for each communist
                                POW->>P: communist.known_affiliations[target.id] = target.party
                            end
                            POW-->>G: target_player

                        else power_name == "five_year_plan"
                            G->>POW: power.execute()
                            POW->>B: policies = [Communist(), Communist(), Liberal()] + policies
                            POW->>B: shuffle(policies)
                            POW-->>G: True

                        else power_name == "congress"
                            G->>POW: power.execute()

                            loop for each communist
                                POW->>P: communist.known_communists = all_communist_ids
                            end
                            POW-->>G: communist_ids

                        else power_name == "radicalization"
                            G->>P: president.choose_player_to_radicalize()
                            P->>ST: strategy.choose_player_to_radicalize(eligible)
                            ST-->>P: target_player
                            P-->>G: target_player
                            G->>POW: power.execute(target_player)

                            alt target_player.is_hitler
                                POW-->>G: None (conversion failed)
                            else
                                POW->>P: target_player.role = Communist()
                                POW->>P: target_player.strategy = CommunistStrategy()
                                POW-->>G: target_player
                            end
                        end
                    end

                    G->>L: log_power_used(power_name, user, target, result)
                end

                %% Avanzar turno
                LP->>G: advance_turn()
                G->>G: set_next_president()
                G->>S: advance_month_counter()
                  LP->>+EP: ElectionPhase(game)
                EP-->>-LP: election_phase
                LP-->>G: election_phase
            end

        else current_phase is GameOverPhase
            %% ===========================================
            %% FASE DE GAME OVER
            %% ===========================================
            Note over GP: 🏁 GAME OVER
            G->>+GP: execute()
            GP->>S: state.game_over = True
            GP-->>-G: self (stays in GameOver)

            Note over G: Game loop ends (game_over = True)
        end
    end

    %% ===========================================
    %% FINALIZACIÓN DEL JUEGO
    %% ===========================================

    Note over G,L: 🎯 FINALIZACIÓN

    G->>L: log_game_end(winner, players, game)
    G-->>-U: state.winner

    %% ===========================================
    %% FLUJOS ESPECIALES
    %% ===========================================

    Note over U,PR: 🔄 FLUJOS ESPECIALES

    %% Oktober Fest Event
        Note over S,P: 🍺 OKTOBER FEST EVENT
        S->>S: month_counter == 10
        S->>S: _start_oktoberfest()

        loop for each bot player
            S->>P: original_strategies[player.id] = player.strategy
            S->>P: player.strategy = RandomStrategy(player)
        end

        Note over S: All bots now use random strategy

        S->>S: month_counter == 11
        S->>S: _end_oktoberfest()

        loop for each bot player
            S->>P: player.strategy = original_strategies[player.id]
        end

    %% Emergency Powers (Article 48 & Enabling Act)
        alt Article48 policy enacted
            G->>+PR: get_power("presidential_propaganda", game)
            PR->>POW: PresidentialPropaganda(game)
            POW-->>PR: power
            PR-->>-G: power
            G->>POW: power.execute()
            POW->>P: president.propaganda_decision(top_policy)
            P-->>POW: discard_decision
            alt discard_decision
                POW->>B: discard(top_policy)
            end
            POW-->>G: top_policy

        else EnablingAct policy enacted
            G->>+PR: get_power("chancellor_propaganda", game)
            PR->>POW: ChancellorPropaganda(game)
            POW-->>PR: power
            PR-->>-G: power
            G->>POW: power.execute()
            POW->>P: chancellor.propaganda_decision(top_policy)
            P-->>POW: discard_decision
            POW-->>G: top_policy
        end

      %% Marked for Execution System

        G->>POW: PresidentialMarkedForExecution.execute(target)
        POW->>S: state.marked_for_execution = target
        POW->>S: state.marked_for_execution_tracker = fascist_track
        POW-->>G: target

        Note over G,S: Each election phase checks marked players
        Note over G,S: _check_marked_for_execution()

        Note over G,S: If fascist_policies_since_marking >= 3:
        Note over G,S: - marked_player.is_dead = True
        Note over G,S: - state.active_players.remove(marked_player)
        Note over G,S: - state.marked_for_execution = None

        Note over G,S: If marked_player.is_hitler:
        Note over G,S: - state.winner = "liberal" or "liberal_and_communist"
        Note over G,S: - Transition to GameOverPhase

```
