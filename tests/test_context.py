# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Context
"""
import pickle
from srgutil.context import Context
from srgutil.context import default_context


def test_context():
    ctx = Context()
    ctx.set("foo", 42)
    child_ctx = ctx.child()
    assert child_ctx.get("foo") == 42

    # Now clobber the local context, and demonstrate
    # that we haven't touched the parent
    child_ctx.set("foo", "bar")
    assert child_ctx.get("foo") == "bar"
    assert child_ctx.get("foo", "batz") == "bar"
    assert ctx.get("foo") == 42
    assert ctx.get("foo", "bar") == 42

    # Revert the child back to the parent value
    child_ctx.delete("foo")
    assert child_ctx.get("foo") == 42

    # Defaults work as expected
    assert child_ctx.get("foo", "bar") == 42


def test_can_pickle():

    ctx = default_context()
    ctx2 = ctx.child()

    c_pickle = pickle.dumps(ctx)
    c2_pickle = pickle.dumps(ctx2)

    pickle.loads(c_pickle)
    pickle.loads(c2_pickle)


def test_default_context():
    ctx = default_context()
    print(ctx)
