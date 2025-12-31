"""Service de mise à jour du modèle de connaissances (BKT)."""


def _clamp01(value: float) -> float:
    """Borne une probabilité dans [0, 1]."""
    return max(0.0, min(1.0, value))


def score_to_correct(score: float, threshold: float = 50.0) -> bool:
    """
    Convertir un score en réussite/échec.
    
    Args:
        score: Score obtenu (0-100)
        threshold: Seuil de réussite
    
    Returns:
        True si réussite, False sinon
    """
    return score >= threshold


def bkt_update(
    p_mastery: float,
    correct: bool,
    p_transit: float,
    p_guess: float,
    p_slip: float,
) -> float:
    """
    Mise à jour Bayesian Knowledge Tracing (BKT).
    
    Args:
        p_mastery: P(L) - Probabilité de maîtrise actuelle
        correct: Observation - réponse correcte ?
        p_transit: P(T) - Probabilité d'apprentissage
        p_guess: P(G) - Probabilité de deviner
        p_slip: P(S) - Probabilité d'erreur d'étourderie
    
    Returns:
        Nouvelle probabilité de maîtrise
    """
    p_mastery = _clamp01(p_mastery)
    p_transit = _clamp01(p_transit)
    p_guess = _clamp01(p_guess)
    p_slip = _clamp01(p_slip)

    if correct:
        # Observation = réponse correcte
        # P(Correct) = P(L)*(1-slip) + (1-P(L))*guess
        denom = (p_mastery * (1.0 - p_slip)) + ((1.0 - p_mastery) * p_guess)
        # Posterior: P(L|Correct) = P(L)*P(Correct|L) / P(Correct)
        p_given_obs = (p_mastery * (1.0 - p_slip)) / denom if denom else p_mastery
    else:
        # Observation = réponse incorrecte
        # P(Incorrect) = P(L)*slip + (1-P(L))*(1-guess)
        denom = (p_mastery * p_slip) + ((1.0 - p_mastery) * (1.0 - p_guess))
        # Posterior: P(L|Incorrect) = P(L)*P(Incorrect|L) / P(Incorrect)
        p_given_obs = (p_mastery * p_slip) / denom if denom else p_mastery

    # Transition (apprentissage entre 2 tentatives)
    p_next = p_given_obs + (1.0 - p_given_obs) * p_transit
    return _clamp01(p_next)


def update_mastery(
    current_level: float,
    score: float,
    *,
    correct: bool = None,
    p_transit: float = 0.15,
    p_guess: float = 0.2,
    p_slip: float = 0.1,
    threshold: float = 50.0,
) -> float:
    """
    Mettre à jour le niveau de maîtrise basé sur un score.
    
    Args:
        current_level: Niveau actuel de maîtrise (0.0 à 1.0)
        score: Score obtenu (0 à 100)
        correct: Réponse correcte ? (si None, déduit du score)
        p_transit: P(T) - Transition/Apprentissage
        p_guess: P(G) - Guess / Deviner
        p_slip: P(S) - Slip / Étourderie
        threshold: Seuil score->correct
    
    Returns:
        Nouveau niveau de maîtrise (0.0 à 1.0)
    """
    # Déterminer si la réponse est correcte
    obs_correct = correct if correct is not None else score_to_correct(score, threshold=threshold)

    # Appliquer BKT
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


def calculate_confidence(
    nb_success: int,
    nb_failures: int,
    streak_correct: int
) -> float:
    """
    Calculer la confiance du système dans l'estimation de maîtrise.
    
    Args:
        nb_success: Nombre de succès
        nb_failures: Nombre d'échecs
        streak_correct: Série de réponses correctes
    
    Returns:
        Score de confiance (0.0 à 1.0)
    """
    total = nb_success + nb_failures
    
    if total == 0:
        return 0.0
    
    # Base de confiance sur le nombre total d'observations
    base_confidence = min(total / 20.0, 0.8)  # Max 0.8 basé sur volume
    
    # Bonus si série de succès
    streak_bonus = min(streak_correct / 10.0, 0.2)  # Max +0.2
    
    return min(base_confidence + streak_bonus, 1.0)