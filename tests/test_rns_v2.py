from pathlib import Path
import pickle
from pprint import pprint
import dataclasses

from recursivenamespace import rns
from recursivenamespace import RecursiveNamespace
from recursivenamespace import utils


PJ_DIR = Path(__file__).parents[1]


data = {
    "n": 1,
    "t": (2, 3),
    "a": [4, [1, 2], {"c5": "555", "c6": "666", "c7": [1, 2, 3]}],
    "s": set([6, "7", 8]),
    "hello": "hello",
    "d": {"e-1": 9, "e-2": {"e_2_1": 10, "e_2_2": (11,)}, "e_3": [12, 13]},
    "v1": "Hello",
    "v2": "World",
}
rns_1 = RecursiveNamespace(data, use_raw_key=False)
rns_2 = RecursiveNamespace(data, use_raw_key=True)


@rns.rns()
@dataclasses.dataclass
class FreeItem:
    v1: str
    v2: int


@dataclasses.dataclass
class SchemaItem:
    v1: str
    v2: int


@rns.rns(use_chain_key=True)
def create_by_chain_key():
    return {"x.y.z": [1, 2, 3], "s": "hello world"}


def test_convert():
    d = dict(rns_1)
    print("dict(rns_1)")
    print(d)
    print("rns_1")
    pprint(rns_1)
    print("rns_2")
    pprint(rns_2)
    # assert:
    assert rns_1.n == d["n"]
    assert rns_1.d.e_1 == d["d"]["e_1"]
    assert rns_2.d["e-1"] == data["d"]["e-1"]


def test_pickle():
    pklpath = PJ_DIR / "out" / "test.pkl"
    if not pklpath.parent.exists():
        pklpath.parent.mkdir()

    # pickel test
    with open(pklpath, "wb") as f:
        pickle.dump(rns_2, f)
    with open(pklpath, "rb") as f:
        rname = pickle.load(f)

    print()
    print("Result after unpickling")
    print(rname)

    assert rns_2 == rname


def test_decorator():
    a = FreeItem("Hello", 1)
    pprint(a)
    assert a.v1 == "Hello"
    assert isinstance(a, RecursiveNamespace)


def test_schema():
    a: SchemaItem = rns_1.as_schema(SchemaItem)
    pprint(a)
    assert a.v1 == "Hello"
    assert a.v2 == "World"
    assert isinstance(a, SchemaItem)


def test_flattern():
    print("RNS object:")
    print(rns_2)
    # 1:
    print("Flatten - RNS")
    pprint(rns_2.to_dict(flatten_sep="."))
    # 2:
    print("Flatten - Json")
    pprint(dict(utils.flatten_as_dict(rns_2.to_dict())))


def test_get_set():
    rns_2["x.y"] = "single-key"
    rns_2.val_set("x.y", "chain-key")
    rns_2.val_set("a[].0", -4)
    rns_2.val_set("a[].1", 100)
    rns_2.val_set("a[].-1.c7[].-1", 10)
    rns_2.val_set("a[].-1.c7[].#", 100)
    rns_2.val_set("a[].#.c7[].#", 100)
    rns_2.val_set("a[].-1.c8", dict(x=123, y="456"))
    rns_2.val_set("a[].-1.c9.c10", dict(x=123, y="456"))
    rns_2.val_set("a[].-1.c9.c11", [dict(x=123, y="456")])
    rns_2.val_set("a[].-1.c9.c11[].#", "a string")

    # debug:
    print(f"===>>>>>> Test case: {test_get_set.__name__}")
    pprint(rns_2)

    assert rns_2["x.y"] == "single-key"
    assert rns_2.val_get(r"x\\.y") == "single-key"
    assert rns_2.val_get("x.y") == "chain-key"
    assert rns_2.val_get("a[].-2.c7[].-2") == 10
    assert rns_2.val_get("a[].-2.c7[].-1") == 100
    assert rns_2.val_get("a[].-1.c7[].-1") == 100
    # assert rns_2.get_or_none("a[].#.c7[].#") == 100


# def main():
#     # print(create_by_chain_key())
#     test_get_set()
#     print("Hello World!")


# if __name__ == "__main__":
#     main()
#     print("..::DONE::..")
