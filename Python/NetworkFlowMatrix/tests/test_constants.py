from networkflowmatrix.network_matrix_data_model import constants


def test_cast_enum() -> None:
    cast_uni = constants.CastType["UNICAST"]

    cast_uni_2 = constants.CastType["UNICAST"]
    cast_multi = constants.CastType["MULTICAST"]
    cast_unkn = constants.CastType["UNKNOWN"]

    assert cast_uni == constants.CastType.UNICAST
    assert cast_uni != constants.CastType.MULTICAST
