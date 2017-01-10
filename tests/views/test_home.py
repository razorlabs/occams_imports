# flake8: noqa

import pytest


class TestIndex:
    def _call_fut(self, *args, **kw):
        from occams_imports.views.home import index as view
        return view(*args, **kw)

    def test_index(self, req):
        response = self._call_fut(None, req)
        assert response == {}
