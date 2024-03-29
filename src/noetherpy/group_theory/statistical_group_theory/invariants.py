"""This module defines several probabilistic invariants related to groups."""

from itertools import (
    combinations,
    combinations_with_replacement,
)
from math import comb
from ..groups import Group
from ..constructions.subgroup_constructions import (
    centralizer,
    normalizer,
)
from ..constructions.subgroup_series import (
    is_nilpotent,
    is_solvable,
)


def commuting_probability(group: Group) -> float:
    """Computes the probability that two elements of the given group commute.

    Args:
        group (Group):

    Returns:
        float: the probability two randomly chosen elements commute.
    """
    return len(group.conjugacy_classes) / group.order


def equal_order_probability(group: Group) -> float:
    """Computes the probability that two elements of the given group have equal orders.

    Args:
        group (Group):

    Returns:
        float: the probability two elements of the group have the same order.
    """
    order_pairs = combinations_with_replacement(group, 2)
    order_equal_count = len(
        [pair for pair in order_pairs if pair[0].order == pair[1].order]
    )
    return order_equal_count / comb(group.order + 1, 2)


def solvable_subgroup_probability(group: Group) -> float:
    """Computes the probability that two randomly chosen elements of the group
    generate a solvable subgroup.

    Args:
        group (Group)

    Returns:
        float: the the probability that two randomly chosen elements of the group
    generate a solvable subgroup.
    """
    group_choose_2_list = combinations(group, 2)
    return (1 / comb(group.order, 2)) * sum(
        (
            is_solvable(group.subgroup_generated_by(gen_set))
            for gen_set in group_choose_2_list
        )
    )


def nilpotent_subgroup_probability(group: Group) -> float:
    """Computes the probability that two randomly chosen elements of the group
    generate a nilpotent subgroup.

    Args:
        group (Group)

    Returns:
        float: the the probability that two randomly chosen elements of the group
    generate a nilpotent subgroup.
    """
    group_choose_2_list = combinations(group, 2)
    return (1 / comb(group.order, 2)) * sum(
        (
            is_nilpotent(group.subgroup_generated_by(gen_set))
            for gen_set in group_choose_2_list
        )
    )


def average_centralizer_size(
    group: Group, k: int, scale_by_order: bool = False
) -> float:
    """Computes the average size of the centralizer generated by k elements.

    Args:
        group (Group)
        k (int): the number of elements to choose randomly from the group.

    Returns:
        float: the average size of the centralizer generated by k elements.
    """
    group_choose_k_list = combinations(group, k)
    order_scaling = (group.order) ** scale_by_order
    return (
        (1 / comb(group.order, k))
        * sum(
            (
                centralizer(group.subgroup_generated_by(gen_set), group).order
                for gen_set in group_choose_k_list
            )
        )
        / order_scaling
    )


def average_normalizer_size(
    group: Group, k: int, scale_by_order: bool = False
) -> float:
    """Computes the average size of the centralizer generated by k elements.

    Args:
        group (Group)
        k (int): the number of elements to choose randomly from the group.

    Returns:
        float: the average size of the centralizer generated by k elements.
    """
    group_choose_k_list = combinations(group, k)
    order_scaling = (group.order) ** scale_by_order
    return (
        (1 / comb(group.order, k))
        * sum(
            (
                normalizer(group.subgroup_generated_by(gen_set), group).order
                for gen_set in group_choose_k_list
            )
        )
        / order_scaling
    )


def expectation_number(k: int, group: Group, scale_by_order: bool = False) -> float:
    """Computes the k-th expectation number of the group. This is
    the average size of the subgroup generated by k distinct elements,
    chosen uniformly randomly from the group.

    Args:
        group (Group)
        k (int): the number of elements to choose randomly.

    Returns:
        float: the k-th expectation number of the group
    """
    group_choose_k_list = combinations(group, k)
    order_scaling = (group.order) ** scale_by_order
    return (
        (1 / comb(group.order, k))
        * sum(
            (
                group.subgroup_generated_by(gen_set).order
                for gen_set in group_choose_k_list
            )
        )
        / order_scaling
    )
