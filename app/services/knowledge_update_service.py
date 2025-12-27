"""Service de mise à jour du modèle de connaissances."""


def _clamp01(value: float) -> float:
    # Utilitaire: borne une probabilité dans [0, 1].
    # En BKT, toutes les quantités manipulées sont des probabilités.
    return max(0.0, min(1.0, value))


def score_to_correct(score: float, threshold: float = 50.0) -> bool:
    # Conversion (simple) score -> réussite.
    # Interprétation: si le score est au moins égal au seuil, on considère que l'observation est "correcte".
    # Tu peux adapter ce seuil selon ta définition de réussite (ex: 70 pour plus strict).
    return score >= threshold


def bkt_update(
    p_mastery: float,  # P(L) - Probabilité de maîtrise (probability of knowing)
    correct: bool,  # Observation: réponse correcte ? (True/False)
    p_transit: float,  # P(T) - Transition/Apprentissage: prob. d'apprendre entre 2 essais
    p_guess: float,  # P(G) - Guess / Deviner: prob. de répondre juste sans maîtriser
    p_slip: float,  # P(S) - Slip / Étourderie: prob. de répondre faux en maîtrisant
) -> float:
    # BKT en 2 étapes:
    # 1) Mise à jour bayésienne P(L | obs) à partir de P(L) et de l'observation (correct/incorrect)
    # 2) Transition d'apprentissage vers l'état suivant: P(L_next) = P(L|obs) + (1 - P(L|obs)) * P(T)
    p_mastery = _clamp01(p_mastery)
    p_transit = _clamp01(p_transit)
    p_guess = _clamp01(p_guess)
    p_slip = _clamp01(p_slip)

    if correct:
        # Observation = réponse correcte.
        # P(Correct) = P(L)*P(Correct|L) + P(~L)*P(Correct|~L)
        #           = P(L)*(1 - slip)     + (1 - P(L))*guess
        denom = (p_mastery * (1.0 - p_slip)) + ((1.0 - p_mastery) * p_guess)
        # Posterior (Bayes):
        # P(L|Correct) = P(L)*P(Correct|L) / P(Correct)
        p_given_obs = (p_mastery * (1.0 - p_slip)) / denom if denom else p_mastery
    else:
        # Observation = réponse incorrecte.
        # P(Incorrect) = P(L)*P(Incorrect|L) + P(~L)*P(Incorrect|~L)
        #             = P(L)*slip            + (1 - P(L))*(1 - guess)
        denom = (p_mastery * p_slip) + ((1.0 - p_mastery) * (1.0 - p_guess))
        # Posterior (Bayes):
        # P(L|Incorrect) = P(L)*P(Incorrect|L) / P(Incorrect)
        p_given_obs = (p_mastery * p_slip) / denom if denom else p_mastery

    # Transition (apprentissage entre 2 tentatives):
    # si l'apprenant ne maîtrisait pas encore, il peut apprendre avec probabilité p_transit.
    p_next = p_given_obs + (1.0 - p_given_obs) * p_transit
    return _clamp01(p_next)


def update_mastery(
    current_level: float,
    score: float,
    *,
    correct: bool | None = None,  # Réponse correcte ? (si None: dérivé de score via threshold)
    p_transit: float = 0.15,  # P(T) - Transition/Apprentissage
    p_guess: float = 0.2,  # P(G) - Guess / Deviner
    p_slip: float = 0.1,  # P(S) - Slip / Étourderie
    threshold: float = 50.0,  # Seuil score->correct (ex: >=50 => correct)
) -> float:
    """
    Mise à jour du niveau de maîtrise basée sur le score obtenu.

    Utilise Bayesian Knowledge Tracing (BKT).

    Args:
        current_level: Niveau actuel de maîtrise (0.0 à 1.0)
        score: Score obtenu (0 à 100)
    Returns:
        Nouveau niveau de maîtrise (0.0 à 1.0)
    """
    # Si l'appelant fournit directement correct=True/False (ex: LearningHistory.success),
    # on l'utilise. Sinon, on le déduit du score via un seuil.
    obs_correct = correct if correct is not None else score_to_correct(score, threshold=threshold)

    # Appliquer la mise à jour BKT (Bayes + transition)
    return bkt_update(
        p_mastery=current_level,
        correct=obs_correct,
        p_transit=p_transit,
        p_guess=p_guess,
        p_slip=p_slip,
    )


def calculate_mastery_from_history(scores: list[float]) -> float:
    """
    Calculer le niveau de maîtrise à partir d'une liste de scores.

    Utilise une moyenne pondérée où les scores récents ont plus de poids.

    Args:
        scores: Liste des scores (0 à 100)

    Returns:
        Niveau de maîtrise calculé (0.0 à 1.0)
    """
    if not scores:
        return 0.2

    p = 0.2
    for s in scores:
        p = update_mastery(p, s)
    return p


def get_mastery_label(mastery_level: float) -> str:
    """
    Obtenir un label textuel pour le niveau de maîtrise.

    Args:
        mastery_level: Niveau de maîtrise (0.0 à 1.0)
    
    Returns:
        Label descriptif
    """
    if mastery_level < 0.2:
        return "Non maîtrisé"
    elif mastery_level < 0.4:
        return "Faiblement maîtrisé"
    elif mastery_level < 0.6:
        return "Partiellement maîtrisé"
    elif mastery_level < 0.8:
        return "Bien maîtrisé"
    else:
        return "Excellemment maîtrisé"
