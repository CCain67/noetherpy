"""This module defines functions for constructing finite abelian groups."""
from functools import reduce

from ..groups import Group
from ..common_groups.cyclic_groups import cyclic_group


def finite_abelian_group_from_order_power_dict(
    order_power_dict: dict, representation: str = "symbolic"
) -> Group:
    """Constructs a finite abelian group from an order_power_dict.

    Args:
        order_power_dict (dict): a dictionary of the form:

        {order: power}

        to construct the group from. For example, the order_power_dict:

        {2:3, 3:1, 7:2}

        produces the group

        (Z/2Z)x(Z/2Z)x(Z/2Z)x(Z/3Z)x(Z/7Z)x(Z/7Z).

    Returns:
        Group: a product of cyclic groups as prescribed by the order_power_dict.
    """
    if representation not in ["symbolic", "permutation", "matrix"]:
        raise ValueError(
            'representation must be one of: "symbolic", "permutation", or "matrix"'
        )
    factors = [
        cyclic_group(N=order, representation=representation) ** power
        for order, power in order_power_dict.items()
    ]
    return reduce(lambda x, y: x * y, factors)
