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

    # Now clobber the local context, and demonstrate
    # that we haven't touched the parent
    assert ctx.get("foo") == 42
    assert ctx.get("foo", "bar") == 42


def test_can_pickle():

    ctx = default_context()
    c_pickle = pickle.dumps(ctx)
    restored = pickle.loads(c_pickle)
    assert restored.__dict__.keys() == ctx.__dict__.keys()


def test_default_context():
    ctx = default_context()
    print(ctx)
