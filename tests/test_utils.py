from pprint import pprint

from recursivenamespace import utils


data = {
    "n": 1,
    "t": (2, 3),
    "a": [4, {"c5": "555", "c6": "666", "c7": [1, 2, 3]}],
    "s": set([6, "7", 8]),
    "hello": "hello",
    "d": {"e-1": 9, "e-2": {"e_2_1": 10, "e_2_2": (11,)}, "e_3": [12, 13]},
    "test": [
        {"hello1": "world"},
        {"hello1": "world"},
        {"hello2": "world"},
        {"hello3": {"a": "hello3", "t": [1, 2, 3]}},
        {"hello3": {"a": "hello3", "t": [4, 5, 6]}},
    ],
    "test2": ["1", "2"],
}


def test_flatten_as_dict():
    out = utils.flatten_as_dict(data, flat_list=True)
    print("utils flatten json:")
    pprint(out)

    assert out["a[].1.c7[].2"] == 3


def test_flatten_as_list_0():
    out = utils.flatten_as_list(data)
    print("utils flatten json as list:")
    pprint(out)

    assert out[2][0] == "a"
    assert out[2][1][0] == 4


def test_flatten_as_list_1():
    out = utils.flatten_as_list(
        data, flat_list_type=utils.FlatListType.WITH_INDEX
    )
    print("utils flatten json as list WITH_INDEX:")
    pprint(out)

    assert out[5][0] == "a[].1.c7[].0"
    assert out[5][1] == 1


def test_flatten_as_list_2():
    out = utils.flatten_as_list(
        data, flat_list_type=utils.FlatListType.WITHOUT_INDEX
    )
    print("utils flatten json as list WITHOUT_INDEX:")
    pprint(out)

    assert out[6][0] == "a[].#.c7[].#"
    assert out[6][1] == 2


def test_flatten_as_list_3():
    out = utils.flatten_as_list(
        data, flat_list_type=utils.FlatListType.WITH_SMART_INDEX
    )
    print("utils flatten json as list WITH_SMART_INDEX:")
    # pprint(out)

    assert out[6][0] == "a[].-1.c7[].#"
    assert out[6][1] == 2

    assert out[22][0] == "test[].#.hello3.a"
    assert out[22][1] == "hello3"

    assert out[23][0] == "test[].-1.hello3.t[].#"
    assert out[23][1] == 4


def main():
    print("Hello World!")
    test_flatten_as_list_3()


if __name__ == "__main__":
    main()
    print("..::DONE::..")
