# Diagrama de Clases Completo - Secret Hitler XL (SHXL)

```mermaid
classDiagram
    %% ===========================================
    %% GAME CORE CLASSES
    %% ===========================================

    class SHXLGame {
        +GameLogger logger
        +GamePhase current_phase
        +EnhancedGameState state
        +bool communists_in_play
        +bool anti_policies_in_play
        +bool emergency_powers_in_play
        +list~int~ human_player_indices
        +str ai_strategy
        +int player_count
        +Player hitler_player
        +bool was_oktoberfest_active
        +int old_month

        +__init__(logger)
        +setup_game(player_count, with_communists, with_anti_policies, with_emergency_powers, human_player_indices, ai_strategy)
        +initialize_board(players, communist_flag)
        +start_game()
        +assign_players()
        +inform_players()
        +_inform_fascists()
        +_inform_communists()
        +choose_first_president()
        +set_next_president()
        +advance_turn()
        +nominate_chancellor()
        +vote_on_government()
        +enact_chaos_policy()
        +check_policy_win()
        +presidential_policy_choice(policies)
        +chancellor_propose_veto()
        +president_veto_accepted()
        +chancellor_policy_choice(policies)
        +get_fascist_power()
        +get_communist_power()
        +execute_power(power_name)
        +execute_presidential_power(power_name)
        +execute_chancellor_power(power_name)
    }

    class EnhancedGameState {
        +bool game_over
        +str winner
        +int round_number
        +list~Player~ players
        +list~Player~ active_players
        +Player president
        +Player president_candidate
        +Player chancellor
        +Player chancellor_candidate
        +int election_tracker
        +list~bool~ last_votes
        +list~Player~ term_limited_players
        +bool special_election
        +int special_election_return_index
        +bool veto_available
        +Policy last_discarded
        +int liberal_track
        +int fascist_track
        +int communist_track
        +list~Player~ investigated_players
        +dict known_communists
        +dict revealed_affiliations
        +list~Player~ marked_for_execution
        +int enacted_policies
        +int marked_for_execution_tracker
        +bool block_next_fascist_power
        +bool block_next_communist_power
        +GameBoard board
        +Policy most_recent_policy
        +list~Policy~ current_policies
        +int month_counter
        +bool oktoberfest_active
        +dict original_strategies
        +dict month_names

        +get_current_month_name()
        +get_month_name(month_number)
        +reset_election_tracker()
        +add_player(player)
        +get_eligible_chancellors()
        +get_next_president_index()
        +handle_player_death(player)
        +advance_month_counter()
        +_start_oktoberfest()
        +_end_oktoberfest()
        +set_next_president()
    }

    class GameBoard {
        +EnhancedGameState state
        +GameLogger logger
        +int player_count
        +bool with_communists
        +int liberal_track_size
        +int fascist_track_size
        +int communist_track_size
        +int liberal_track
        +int fascist_track
        +int communist_track
        +list~Policy~ policies
        +list~Policy~ discards
        +list~str~ fascist_powers
        +list~str~ communist_powers
        +bool veto_available

        +__init__(game_state, player_count, with_communists, logger)
        +_get_communist_track_size()
        +_setup_fascist_powers()
        +_setup_communist_powers()
        +initialize_policy_deck(policy_factory, with_anti_policies, with_emergency)
        +draw_policy(count)
        +discard(policies)
        +enact_policy(policy, is_chaos, emergency_powers_in_play, anti_policies_in_play)
        +_handle_anti_policy(policy)
        +_handle_emergency_policy(policy)
        +get_fascist_power()
        +get_communist_power()
        +check_win_condition()
        +shuffle_policies()
    }

    class GameLogger {
        +LogLevel level
        +logging.Logger logger
        +dict policy_stats
        +int election_count
        +int failed_elections

        +__init__(level)
        +log(message, level)
        +log_game_setup(game, level)
        +log_election(president, chancellor, votes, passed, active_players)
        +log_policy_enacted(policy, president, chancellor)
        +log_power_used(power_name, user, target, result)
        +log_player_death(player)
        +log_policy_deck(policies)
        +log_shuffle(policies)
        +log_veto_proposed(chancellor)
        +log_veto_accepted(president)
        +log_chaos_policy(policy)
        +log_game_over(winner)
    }

    class LogLevel {
        <<enumeration>>
        NONE
        MINIMAL
        NORMAL
        VERBOSE
        DEBUG
    }

    %% ===========================================
    %% GAME PHASES
    %% ===========================================

    class GamePhase {
        <<abstract>>
        +SHXLGame game

        +__init__(game)
        +execute()* GamePhase
    }

    class SetupPhase {
        +execute() GamePhase
    }

    class ElectionPhase {
        +execute() GamePhase
        +_check_marked_for_execution()
    }

    class LegislativePhase {
        +execute() GamePhase
    }

    class GameOverPhase {
        +execute() GamePhase
    }

    %% ===========================================
    %% PLAYER CLASSES
    %% ===========================================

    class Player {
        <<abstract>>
        +int id
        +str name
        +Role role
        +EnhancedGameState state
        +bool is_dead
        +int player_count
        +Player hitler
        +list~Player~ fascists
        +list~int~ known_communists
        +dict inspected_players
        +dict known_affiliations

        +__init__(id, name, role, state)
        +is_fascist bool
        +is_liberal bool
        +is_communist bool
        +is_hitler bool
        +knows_hitler bool
        +__repr__()
        +initialize_role_attributes()
        +nominate_chancellor()* Player
        +filter_policies(policies)* tuple
        +choose_policy(policies)* tuple
        +vote()* bool
        +veto()* bool
        +accept_veto()* bool
        +view_policies(policies)*
        +kill()* Player
        +choose_player_to_mark()* Player
        +inspect_player()* Player
        +choose_next()* Player
        +choose_player_to_radicalize()* Player
        +propaganda_decision(policy)* bool
        +choose_revealer(eligible_players)* Player
        +social_democratic_removal_choice(state)* str
    }

    class AIPlayer {
        +PlayerStrategy strategy
        +list~Policy~ peeked_policies

        +__init__(id, name, role, state, strategy_type)
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote() bool
        +veto() bool
        +accept_veto() bool
        +view_policies(policies)
        +kill() Player
        +choose_player_to_mark() Player
        +inspect_player() Player
        +choose_next() Player
        +choose_player_to_radicalize() Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +social_democratic_removal_choice(state) str
    }

    class HumanPlayer {
        +_display_players(players)
        +_get_player_choice(players, action_name) Player
        +_display_role_info()
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote() bool
        +veto() bool
        +accept_veto() bool
        +view_policies(policies)
        +kill() Player
        +choose_player_to_mark() Player
        +inspect_player() Player
        +choose_next() Player
        +choose_player_to_radicalize() Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +social_democratic_removal_choice(state) str
    }

    class PlayerFactory {
        +create_player(id, name, role, state, strategy_type, player_type)$ Player
        +apply_strategy_to_player(player, strategy_type)
        +update_player_strategies(players, strategy_type)
        +create_players(count, state, strategy_type, human_player_indices) list~Player~
    }

    %% ===========================================
    %% PLAYER STRATEGIES
    %% ===========================================

    class PlayerStrategy {
        <<abstract>>
        +Player player

        +__init__(player)
        +nominate_chancellor(eligible_players)* Player
        +filter_policies(policies)* tuple
        +choose_policy(policies)* tuple
        +vote(president, chancellor)* bool
        +veto(policies)* bool
        +accept_veto(policies)* bool
        +choose_player_to_kill(eligible_players)* Player
        +choose_player_to_inspect(eligible_players)* Player
    }

    class RandomStrategy {
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote(president, chancellor) bool
        +veto(policies) bool
        +accept_veto(policies) bool
        +choose_player_to_kill(eligible_players) Player
        +choose_player_to_inspect(eligible_players) Player
        +choose_next_president(eligible_players) Player
        +choose_player_to_radicalize(eligible_players) Player
        +choose_player_to_mark(eligible_players) Player
        +choose_player_to_bug(eligible_players) Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +pardon_player() bool
        +chancellor_veto_proposal(policies) bool
        +vote_of_no_confidence() bool
        +social_democratic_removal_choice() str
    }

    class LiberalStrategy {
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote(president, chancellor) bool
        +veto(policies) bool
        +accept_veto(policies) bool
        +choose_player_to_kill(eligible_players) Player
        +choose_player_to_inspect(eligible_players) Player
        +choose_next_president(eligible_players) Player
        +choose_player_to_radicalize(eligible_players) Player
        +choose_player_to_mark(eligible_players) Player
        +choose_player_to_bug(eligible_players) Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +pardon_player() bool
        +chancellor_veto_proposal(policies) bool
        +vote_of_no_confidence() bool
        +social_democratic_removal_choice() str
    }

    class FascistStrategy {
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote(president, chancellor) bool
        +veto(policies) bool
        +accept_veto(policies) bool
        +choose_player_to_kill(eligible_players) Player
        +choose_player_to_inspect(eligible_players) Player
        +choose_next_president(eligible_players) Player
        +choose_player_to_radicalize(eligible_players) Player
        +choose_player_to_mark(eligible_players) Player
        +choose_player_to_bug(eligible_players) Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +pardon_player() bool
        +chancellor_veto_proposal(policies) bool
        +vote_of_no_confidence() bool
        +social_democratic_removal_choice() str
    }

    class CommunistStrategy {
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote(president, chancellor) bool
        +veto(policies) bool
        +accept_veto(policies) bool
        +choose_player_to_kill(eligible_players) Player
        +choose_player_to_inspect(eligible_players) Player
        +choose_next_president(eligible_players) Player
        +choose_player_to_radicalize(eligible_players) Player
        +choose_player_to_mark(eligible_players) Player
        +choose_player_to_bug(eligible_players) Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +pardon_player() bool
        +chancellor_veto_proposal(policies) bool
        +vote_of_no_confidence() bool
        +social_democratic_removal_choice() str
    }

    class SmartStrategy {
        +nominate_chancellor(eligible_players) Player
        +filter_policies(policies) tuple
        +choose_policy(policies) tuple
        +vote(president, chancellor) bool
        +veto(policies) bool
        +accept_veto(policies) bool
        +choose_player_to_kill(eligible_players) Player
        +choose_player_to_inspect(eligible_players) Player
        +choose_next_president(eligible_players) Player
        +choose_player_to_radicalize(eligible_players) Player
        +choose_player_to_mark(eligible_players) Player
        +choose_player_to_bug(eligible_players) Player
        +propaganda_decision(policy) bool
        +choose_revealer(eligible_players) Player
        +pardon_player() bool
        +chancellor_veto_proposal(policies) bool
        +vote_of_no_confidence() bool
        +social_democratic_removal_choice() str
    }

    %% ===========================================
    %% ROLES
    %% ===========================================

    class Role {
        +str party_membership
        +str role

        +__init__()
        +__repr__()
    }

    class Liberal {
        +__init__()
    }

    class Fascist {
        +__init__()
    }

    class Hitler {
        +__init__()
    }

    class Communist {
        +__init__()
    }

    class RoleFactory {
        +get_role_counts(player_count, with_communists)$ dict
        +create_roles(player_count, with_communists)$ list~Role~
    }

    %% ===========================================
    %% POLICIES
    %% ===========================================

    class Policy {
        +str type

        +__init__(type)
        +__repr__()
    }

    class FascistPolicy {
        +__init__()
    }

    class LiberalPolicy {
        +__init__()
    }

    class CommunistPolicy {
        +__init__()
    }

    class AntiFascist {
        +__init__()
    }

    class AntiCommunist {
        +__init__()
    }

    class SocialDemocratic {
        +__init__()
    }

    class Article48 {
        +__init__()
    }

    class EnablingAct {
        +__init__()
    }

    class PolicyFactory {
        +create_policy_deck(player_count, with_communists, with_anti_policies, with_emergency_powers)$ list~Policy~
    }

    %% ===========================================
    %% POWERS
    %% ===========================================

    class PowerOwner {
        <<enumeration>>
        PRESIDENT
        CHANCELLOR
    }

    class Power {
        <<abstract>>
        +SHXLGame game

        +__init__(game)
        +execute(*args, **kwargs)* object
        +get_owner()$ PowerOwner
    }

    %% Fascist Powers
    class InvestigateLoyalty {
        +execute(target_player) str
    }

    class SpecialElection {
        +execute(next_president) Player
    }

    class PolicyPeek {
        +execute() list~Policy~
    }

    class Execution {
        +execute(target_player) Player
    }

    %% Communist Powers
    class Confession {
        +execute() str
    }

    class Bugging {
        +execute(target_player) Player
    }

    class FiveYearPlan {
        +execute() bool
    }

    class Congress {
        +execute() list~int~
    }

    class Radicalization {
        +execute(target_player) Player
    }

    class Propaganda {
        +execute() Policy
    }

    class Impeachment {
        +execute(target_player, revealer_player) bool
    }

    %% Article 48 Powers (Presidential Emergency)
    class Article48Power {
        <<abstract>>
        +get_owner()$ PowerOwner
    }

    class PresidentialPropaganda {
        +execute() Policy
    }

    class PresidentialPolicyPeek {
        +execute() list~Policy~
    }

    class PresidentialImpeachment {
        +execute(target_player, revealer_player) bool
    }

    class PresidentialMarkedForExecution {
        +execute(target_player) Player
    }

    class PresidentialExecution {
        +execute(target_player) Player
    }

    class PresidentialPardon {
        +execute() Player
    }

    %% Enabling Act Powers (Chancellor Emergency)
    class EnablingActPower {
        <<abstract>>
        +get_owner()$ PowerOwner
    }

    class ChancellorPropaganda {
        +execute() Policy
    }

    class ChancellorPolicyPeek {
        +execute() list~Policy~
    }

    class ChancellorImpeachment {
        +execute(revealer_player) bool
    }

    class ChancellorMarkedForExecution {
        +execute(target_player) Player
    }

    class ChancellorExecution {
        +execute(target_player) Player
    }

    class VoteOfNoConfidence {
        +execute() Policy
    }

    class PowerRegistry {
        +get_power(power_name, game)$ Power
        +get_owner(power_name)$ PowerOwner
        +get_all_fascist_powers()$ list~str~
        +get_all_communist_powers()$ list~str~
        +get_all_article48_powers()$ list~str~
        +get_all_enabling_act_powers()$ list~str~
    }

    %% ===========================================
    %% RELATIONSHIPS
    %% ===========================================    %% Game Core Relationships
    SHXLGame -- EnhancedGameState : contains
    SHXLGame -- GameLogger : uses
    SHXLGame -- GamePhase : current_phase
    EnhancedGameState -- GameBoard : contains
    EnhancedGameState --o Player : president
    EnhancedGameState --o Player : chancellor
    EnhancedGameState *--* Player : players
    EnhancedGameState *--* Policy : current_policies
    GameBoard *--* Policy : policies
    GameBoard *--* Policy : discards
    GameLogger -- LogLevel : level    %% Phase Relationships
    GamePhase <|-- SetupPhase
    GamePhase <|-- ElectionPhase
    GamePhase <|-- LegislativePhase
    GamePhase <|-- GameOverPhase
    GamePhase -- SHXLGame : game

    %% Player Relationships
    Player <|-- AIPlayer
    Player <|-- HumanPlayer
    Player -- Role : role
    Player -- EnhancedGameState : state
    AIPlayer -- PlayerStrategy : strategy
    PlayerFactory ..> Player : creates
    PlayerFactory ..> AIPlayer : creates
    PlayerFactory ..> HumanPlayer : creates

    %% Strategy Relationships
    PlayerStrategy <|-- RandomStrategy
    PlayerStrategy <|-- LiberalStrategy
    PlayerStrategy <|-- FascistStrategy
    PlayerStrategy <|-- CommunistStrategy
    PlayerStrategy <|-- SmartStrategy
    PlayerStrategy -- Player : player

    %% Role Relationships
    Role <|-- Liberal
    Role <|-- Fascist
    Role <|-- Hitler
    Role <|-- Communist
    RoleFactory ..> Role : creates    %% Policy Relationships
    Policy <|-- FascistPolicy
    Policy <|-- LiberalPolicy
    Policy <|-- CommunistPolicy
    Policy <|-- AntiFascist
    Policy <|-- AntiCommunist
    Policy <|-- SocialDemocratic
    Policy <|-- Article48
    Policy <|-- EnablingAct
    PolicyFactory ..> Policy : creates

    %% Power Relationships
    Power <|-- InvestigateLoyalty
    Power <|-- SpecialElection
    Power <|-- PolicyPeek
    Power <|-- Execution
    Power <|-- Confession
    Power <|-- Bugging
    Power <|-- FiveYearPlan
    Power <|-- Congress
    Power <|-- Radicalization
    Power <|-- Propaganda
    Power <|-- Impeachment

    Power <|-- Article48Power
    Article48Power <|-- PresidentialPropaganda
    Article48Power <|-- PresidentialPolicyPeek
    Article48Power <|-- PresidentialImpeachment
    Article48Power <|-- PresidentialMarkedForExecution
    Article48Power <|-- PresidentialExecution
    Article48Power <|-- PresidentialPardon

    Power <|-- EnablingActPower
    EnablingActPower <|-- ChancellorPropaganda
    EnablingActPower <|-- ChancellorPolicyPeek
    EnablingActPower <|-- ChancellorImpeachment
    EnablingActPower <|-- ChancellorMarkedForExecution
    EnablingActPower <|-- ChancellorExecution
    EnablingActPower <|-- VoteOfNoConfidence
      Power -- SHXLGame : game
    Power -- PowerOwner : owner
    PowerRegistry ..> Power : creates

    %% Factory Relationships
    SHXLGame ..> PlayerFactory : uses
    SHXLGame ..> RoleFactory : uses
    SHXLGame ..> PolicyFactory : uses
    SHXLGame ..> PowerRegistry : uses
```
