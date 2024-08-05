(define (domain hanoi_parts_3)
(:requirements :strips :typing)
(:types
    disc peg - stackable
)
(:predicates 
(clear ?disc - stackable)
(on ?discsm - disc ?disclg - stackable) 
(smaller ?disclg - stackable ?discsm - disc) 
(over ?disc - stackable) 
(grasped ?disc - stackable)
(free)
)



(:action reach_pick
:parameters (?from - stackable ?to - stackable)
:precondition (and 
    (clear ?to)
    (free)
    (over ?from)
    )
:effect (and 
	(over ?to) 
	(not (over ?from)))
)

(:action reach_drop
:parameters (?disc - disc ?from - stackable ?to - stackable)
:precondition (and 
    (grasped ?disc) 
    (clear ?to) 
    (over ?from)
    )
:effect (and 
    (over ?to) 
    (not (over ?from))
    )
)

(:action pick
:parameters (?disc - disc ?from - stackable)
:precondition (and 
    (clear ?disc)
    (over ?disc) 
    (on ?disc ?from)
    (free)
    )
:effect (and 
    (grasped ?disc) 
    (not (clear ?disc))
    (not (on ?disc ?from))
    (not (free))
    (not (over ?disc))
    (over ?from)
    (clear ?from)
    )
)

(:action drop
:parameters (?disc - disc ?to - stackable)
:precondition (and 
    (over ?to) 
    (grasped ?disc) 
    (clear ?to) 
    (smaller ?to ?disc)
    )
:effect (and 
    (not (grasped ?disc)) 
    (not (clear ?to)) 
    (clear ?disc) 
    (on ?disc ?to) 
    (free)
    )
)
)
