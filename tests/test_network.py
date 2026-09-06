"""Network Event v1 twin — no crisis/×3 side effects."""

from __future__ import annotations

import json
import os
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from bot.main import _Health
from bot import network as net


@pytest.fixture()
ndef http_port(monkeypatch):
    monkeypatch.delenv("NETWORK_SECRET", raising=False)
    monkeypatch.setenv("NODE_ID", "protocollo-rosso")
    monkeypatch.delenv("NETWORK_PEERS", raising=False)
    net._recent.clear()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Health)
    port = server.server_address[1]
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield port
    server.shutdown()


def _get(port: int, path: str) -> tuple[int, bytes]:
    with urlopen(f"http://127.0.0.1:{port}{path}", timeout=3) as r:
        return r.status, r.read()


def _post(port: int, path: str, body: dict, headers: dict | None = None) -> tuple[int, bytes]:
    data = json.dumps(body).encode("utf-8")
    req = Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urlopen(req, timeout=3) as r:
            return r.status, r.read()
    except HTTPError as e:
        return e.code, e.read()


def test_health(http_port):
    status, body = _get(http_port, "/health")
    assert status == 200
    assert b"protocollo-rosso" in body.lower() or b"ok" in body.lower()


def test_nodes(http_port):
    status, body = _get(http_port, "/network/v1/nodes")
    assert status == 200
    data = json.loads(body.decode("utf-8"))
    assert data["nodeId"] == "protocollo-rosso"
    assert isinstance(data["peers"], list)
    assert isinstance(data["recent"], list)


def test_event_ingest(http_port):
    ev = net.create_network_event("ping", {"hello": True})
    status, _ = _post(http_port, "/network/v1/event", ev)
    assert status == 204
    status, body = _get(http_port, "/network/v1/nodes")
    recent = json.loads(body.decode("utf-8"))["recent"]
    assert any(r.get("id") == ev["id"] for r in recent)


def test_event_bad_json(http_port):
    req = Request(
        f"http://127.0.0.1:{http_port}/network/v1/event",
        data=b"not-json",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with pytest.raises(HTTPError) as ei:
        urlopen(req, timeout=3)
    assert ei.value.code == 400
