from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.wsgi import create_wsgi_app


def main():
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    app = create_wsgi_app()

    try:
        from waitress import serve
    except ImportError as exc:
        raise SystemExit("waitress is not installed. Run: py -3 -m pip install -r .\\requirements.txt") from exc

    print(f"Starting production server on http://{host}:{port} (APP_ENV={os.getenv('APP_ENV', 'production')})")
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
