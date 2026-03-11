import argparse
import logging
import os
import signal
import sys
import uvicorn

from ai_node.lifecycle.node_lifecycle import NodeLifecycle
from ai_node.runtime.node_control_api import NodeControlState, create_node_control_app


LOGGER = logging.getLogger("ai_node.main")
SHOULD_STOP = False


def _handle_signal(signum, _frame):
    global SHOULD_STOP
    LOGGER.info("received signal %s, stopping", signum)
    SHOULD_STOP = True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthia AI Node backend entrypoint")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one startup cycle and exit (for smoke checks)",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=5.0,
        help="Heartbeat interval while running",
    )
    parser.add_argument(
        "--api-host",
        default=os.environ.get("SYNTHIA_API_HOST", "127.0.0.1"),
        help="Node control API host",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=int(os.environ.get("SYNTHIA_API_PORT", "9002")),
        help="Node control API port",
    )
    parser.add_argument(
        "--bootstrap-config-path",
        default=os.environ.get("SYNTHIA_BOOTSTRAP_CONFIG_PATH", ".run/bootstrap_config.json"),
        help="Path for persisted bootstrap setup config",
    )
    return parser


def run(
    *,
    once: bool,
    interval_seconds: float,
    api_host: str = "127.0.0.1",
    api_port: int = 9002,
    bootstrap_config_path: str = ".run/bootstrap_config.json",
) -> int:
    LOGGER.info("starting ai-node backend")
    lifecycle = NodeLifecycle(logger=LOGGER)
    control_state = NodeControlState(
        lifecycle=lifecycle,
        config_path=bootstrap_config_path,
        logger=LOGGER,
    )
    app = create_node_control_app(state=control_state, logger=LOGGER)
    LOGGER.info("phase1 modules loaded; control API active")

    if once:
        LOGGER.info("run-once mode complete")
        return 0

    uvicorn.run(app, host=api_host, port=api_port, log_level="info")
    LOGGER.info("backend stopped cleanly")
    return 0


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    args = build_parser().parse_args()
    return run(
        once=args.once,
        interval_seconds=args.interval_seconds,
        api_host=args.api_host,
        api_port=args.api_port,
        bootstrap_config_path=args.bootstrap_config_path,
    )


if __name__ == "__main__":
    sys.exit(main())
