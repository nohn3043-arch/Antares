"""GFSIP/1.0 QUIC Transport (Section 6.1).

Real QUIC transport using aioquic. Replaces the in-memory Link for
production / cross-machine use.

  ALPN         : gfsip/1
  Framing      : 4-byte big-endian uint32 length prefix + GFSIP frame
  Stream model : single bidirectional QUIC stream per GFSIP session

Usage (client)::

    from gfsip.quic_transport import quic_connect
    link = await quic_connect("127.0.0.1", 4433)
    await link.send_frame(frame_bytes)
    reply = await link.recv_frame()
    await link.close()

Usage (server)::

    from gfsip.quic_transport import QuicServer
    server = QuicServer("0.0.0.0", 4433)
    await server.start()
    link = await server.accept()
    frame = await link.recv_frame()
    await link.send_frame(reply_bytes)
    await server.stop()
"""

import asyncio
import os
import ssl
import tempfile
from typing import Optional, Tuple

from aioquic.asyncio import QuicConnectionProtocol, connect, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

# ── constants ───────────────────────────────────────────────
GFSIP_ALPN = "gfsip/1"
_FRAME_PREFIX_SIZE = 4  # 4-byte big-endian uint32


# ── certificate helpers ─────────────────────────────────────
def _generate_self_signed_cert() -> Tuple[str, str]:
    """Generate a temporary self-signed cert + key (testing).

    Includes subjectAltName for localhost / 127.0.0.1 as required by aioquic.
    Returns (cert_path, key_path) in a fresh temp directory.
    Caller is responsible for cleanup.
    """
    import ipaddress
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "gfsip.local"),
    ])
    now = datetime.datetime.utcnow()
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("gfsip.local"),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                x509.IPAddress(ipaddress.ip_address("::1")),
            ]),
            critical=False,
        )
    )
    cert = cert_builder.sign(key, hashes.SHA256())

    tmpdir = tempfile.mkdtemp(prefix="gfsip-quic-")
    cert_path = os.path.join(tmpdir, "cert.pem")
    key_path = os.path.join(tmpdir, "key.pem")

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ))
    return cert_path, key_path


# ── stream read helper ──────────────────────────────────────
async def _read_exact(stream, n: int) -> bytes:
    """Read exactly n bytes from an aioquic QuicStream (handles partial reads)."""
    chunks = []
    remaining = n
    while remaining > 0:
        data = await stream.read(remaining)
        if not data:
            raise ConnectionError("QUIC stream closed before enough data arrived")
        chunks.append(data)
        remaining -= len(data)
    return b"".join(chunks)


# ── QuicLink ─────────────────────────────────────────────────
class QuicLink:
    """A single GFSIP-over-QUIC session.

    Wraps an aioquic QuicConnectionProtocol + (StreamReader, StreamWriter)
    pair and exposes length-prefixed frame send/recv.
    """

    def __init__(self, protocol: QuicConnectionProtocol, reader, writer,
                 context_manager=None):
        self._protocol = protocol
        self._reader = reader
        self._writer = writer
        self._context_manager = context_manager
        self._closed = False

    async def send_frame(self, data: bytes) -> None:
        """Send one GFSIP frame (4-byte length prefix + payload)."""
        if self._closed:
            raise ConnectionError("QuicLink is closed")
        prefix = len(data).to_bytes(_FRAME_PREFIX_SIZE, "big")
        self._writer.write(prefix + data)
        self._protocol.transmit()

    async def recv_frame(self) -> bytes:
        """Receive one complete GFSIP frame (reads prefix + exact payload)."""
        if self._closed:
            raise ConnectionError("QuicLink is closed")
        prefix = await _read_exact(self._reader, _FRAME_PREFIX_SIZE)
        length = int.from_bytes(prefix, "big")
        if length == 0:
            return b""
        return await _read_exact(self._reader, length)

    async def close(self) -> None:
        """Gracefully close the QUIC connection."""
        if self._closed:
            return
        self._closed = True
        try:
            self._writer.close()
            self._protocol.transmit()
        except Exception:
            pass
        try:
            self._protocol.close()
        except Exception:
            pass
        # Exit the aioquic connect() context manager if we own it
        if self._context_manager is not None:
            try:
                await self._context_manager.__aexit__(None, None, None)
            except Exception:
                pass
            self._context_manager = None

    def pending(self) -> bool:
        """Non-blocking check whether received data is buffered."""
        if self._closed:
            return False
        # asyncio.StreamReader buffers incoming bytes in _buffer
        buf = getattr(self._reader, "_buffer", None)
        if buf is not None:
            return len(buf) > 0
        return False

    @property
    def closed(self) -> bool:
        return self._closed


# ── client ───────────────────────────────────────────────────
async def quic_connect(host: str, port: int, *,
                       verify_cert: bool = False,
                       cert_path: Optional[str] = None) -> QuicLink:
    """Connect to a GFSIP/QUIC server and return a QuicLink.

    Args:
        host: Server hostname or IP address.
        port: Server UDP port.
        verify_cert: If True, verify the server certificate against system CAs.
                     Default False (self-signed / testing).
        cert_path: Optional path to a CA certificate file for verification.
    """
    config = QuicConfiguration(is_client=True, alpn_protocols=[GFSIP_ALPN])
    if verify_cert:
        if cert_path:
            config.load_verify_locations(cert_path)
    else:
        config.verify_mode = ssl.CERT_NONE  # skip cert verification (testing)

    # aioquic connect() is an async context manager; enter it manually
    # so the connection stays alive after this function returns.
    cm = connect(host, port, configuration=config)
    protocol = await cm.__aenter__()
    # aioquic create_stream() returns (StreamReader, StreamWriter)
    reader, writer = await protocol.create_stream()
    return QuicLink(protocol, reader, writer, context_manager=cm)


# ── server protocol ──────────────────────────────────────────
class _GfsipServerProtocol(QuicConnectionProtocol):
    """Server-side protocol that captures its own reference for new streams.

    aioquic's stream_handler only passes (reader, writer), not the protocol.
    We override quic_event_received to install a closure that captures self,
    so the accept queue gets (protocol, reader, writer) tuples.
    """

    def __init__(self, *args, accept_queue: asyncio.Queue, **kwargs):
        super().__init__(*args, **kwargs)
        self._accept_queue = accept_queue

    def quic_event_received(self, event):
        # Install a stream_handler closure that captures this protocol instance.
        # aioquic calls self._stream_handler(reader, writer) on new streams.
        self._stream_handler = lambda reader, writer: self._accept_queue.put_nowait(
            (self, reader, writer)
        )
        super().quic_event_received(event)


# ── server ───────────────────────────────────────────────────
class QuicServer:
    """GFSIP/QUIC server.

    Generates a self-signed cert on start(), listens on UDP, and
    yields QuicLink objects via accept(). Uses aioquic's stream_handler
    callback to detect incoming bidirectional streams.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 4433):
        self.host = host
        self.port = port
        self._cert_path: Optional[str] = None
        self._key_path: Optional[str] = None
        self._server = None
        self._accept_queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        """Generate cert and start listening."""
        self._cert_path, self._key_path = _generate_self_signed_cert()
        config = QuicConfiguration(is_client=False, alpn_protocols=[GFSIP_ALPN])
        config.load_cert_chain(self._cert_path, self._key_path)

        # Use custom protocol class so we can capture the protocol reference
        # when new streams are opened (aioquic stream_handler doesn't pass it).
        def _factory(*args, **kwargs):
            return _GfsipServerProtocol(*args, accept_queue=self._accept_queue, **kwargs)

        # aioquic serve() is a plain coroutine returning a server object
        self._server = await serve(self.host, self.port,
                                    configuration=config,
                                    create_protocol=_factory)

    async def accept(self) -> QuicLink:
        """Wait for the next incoming GFSIP session."""
        protocol, reader, writer = await self._accept_queue.get()
        return QuicLink(protocol, reader, writer)

    async def stop(self) -> None:
        """Stop listening and clean up temp cert files."""
        if self._server:
            try:
                self._server.close()
                await self._server.wait_closed()
            except Exception:
                pass
            self._server = None
        # Remove temp cert + key + directory
        tmpdir = None
        for path in (self._cert_path, self._key_path):
            if path:
                if tmpdir is None:
                    tmpdir = os.path.dirname(path)
                try:
                    os.unlink(path)
                except OSError:
                    pass
        if tmpdir:
            try:
                os.rmdir(tmpdir)
            except OSError:
                pass
        self._cert_path = None
        self._key_path = None
