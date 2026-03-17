from __future__ import annotations

import argparse
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from rpc_service import NotebookRPCService


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    daemon_threads = True
    allow_reuse_address = True


def build_server(host: str, port: int, xml_path: str) -> ThreadedXMLRPCServer:
    server = ThreadedXMLRPCServer(
        (host, port),
        requestHandler=RequestHandler,
        allow_none=True,
        logRequests=True,
    )
    service = NotebookRPCService(xml_path)
    server.register_introspection_functions()
    server.register_instance(service)
    return server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Threaded XML-RPC notebook server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host address")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--xml", default="database.xml", help="XML database file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = build_server(args.host, args.port, args.xml)
    print(f"Notebook RPC server is running on http://{args.host}:{args.port}/RPC2")
    print(f"XML database file: {args.xml}")
    print("Press Ctrl+C to stop the server.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutdown requested by user.")
    finally:
        server.server_close()
        print("Server stopped cleanly.")


if __name__ == "__main__":
    main()
