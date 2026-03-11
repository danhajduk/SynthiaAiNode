import argparse
import logging
import signal
import sys
import time


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
    return parser


def run(*, once: bool, interval_seconds: float) -> int:
    LOGGER.info("starting ai-node backend")
    LOGGER.info("phase1 modules loaded; runtime orchestration not yet fully wired")

    if once:
        LOGGER.info("run-once mode complete")
        return 0

    while not SHOULD_STOP:
        LOGGER.info("backend heartbeat")
        time.sleep(interval_seconds)

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
    return run(once=args.once, interval_seconds=args.interval_seconds)


if __name__ == "__main__":
    sys.exit(main())
