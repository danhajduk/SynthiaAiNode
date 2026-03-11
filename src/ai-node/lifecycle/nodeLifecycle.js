export const NODE_LIFECYCLE_STATES = Object.freeze({
  UNCONFIGURED: "unconfigured",
  BOOTSTRAP_CONNECTING: "bootstrap_connecting",
  BOOTSTRAP_CONNECTED: "bootstrap_connected",
  CORE_DISCOVERED: "core_discovered",
  REGISTRATION_PENDING: "registration_pending",
  PENDING_APPROVAL: "pending_approval",
  TRUSTED: "trusted",
  CAPABILITY_SETUP_PENDING: "capability_setup_pending",
  OPERATIONAL: "operational",
  DEGRADED: "degraded",
});

const ALLOWED_TRANSITIONS = new Map([
  [NODE_LIFECYCLE_STATES.UNCONFIGURED, new Set([NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTING])],
  [NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTING, new Set([NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTED])],
  [NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTED, new Set([NODE_LIFECYCLE_STATES.CORE_DISCOVERED])],
  [NODE_LIFECYCLE_STATES.CORE_DISCOVERED, new Set([NODE_LIFECYCLE_STATES.REGISTRATION_PENDING])],
  [NODE_LIFECYCLE_STATES.REGISTRATION_PENDING, new Set([NODE_LIFECYCLE_STATES.PENDING_APPROVAL])],
  [NODE_LIFECYCLE_STATES.PENDING_APPROVAL, new Set([NODE_LIFECYCLE_STATES.TRUSTED])],
  [NODE_LIFECYCLE_STATES.TRUSTED, new Set([NODE_LIFECYCLE_STATES.CAPABILITY_SETUP_PENDING])],
  [NODE_LIFECYCLE_STATES.CAPABILITY_SETUP_PENDING, new Set([NODE_LIFECYCLE_STATES.OPERATIONAL])],
  [NODE_LIFECYCLE_STATES.OPERATIONAL, new Set([])],
  [NODE_LIFECYCLE_STATES.DEGRADED, new Set([NODE_LIFECYCLE_STATES.OPERATIONAL])],
]);

const STATE_VALUES = new Set(Object.values(NODE_LIFECYCLE_STATES));
const DEGRADABLE_STATES = new Set([
  NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTING,
  NODE_LIFECYCLE_STATES.BOOTSTRAP_CONNECTED,
  NODE_LIFECYCLE_STATES.CORE_DISCOVERED,
  NODE_LIFECYCLE_STATES.REGISTRATION_PENDING,
  NODE_LIFECYCLE_STATES.PENDING_APPROVAL,
  NODE_LIFECYCLE_STATES.TRUSTED,
  NODE_LIFECYCLE_STATES.CAPABILITY_SETUP_PENDING,
  NODE_LIFECYCLE_STATES.OPERATIONAL,
]);

function canTransition(from, to) {
  if (to === NODE_LIFECYCLE_STATES.DEGRADED && DEGRADABLE_STATES.has(from)) {
    return true;
  }
  return ALLOWED_TRANSITIONS.get(from)?.has(to) === true;
}

export function createNodeLifecycle(options = {}) {
  const logger = options.logger ?? console;
  const onTransition = options.onTransition ?? (() => {});
  let state = NODE_LIFECYCLE_STATES.UNCONFIGURED;

  return {
    getState() {
      return state;
    },
    canTransitionTo(nextState) {
      return canTransition(state, nextState);
    },
    transitionTo(nextState, meta = {}) {
      if (!STATE_VALUES.has(nextState)) {
        throw new Error(`unknown lifecycle state: ${nextState}`);
      }
      if (!canTransition(state, nextState)) {
        throw new Error(`invalid state transition: ${state} -> ${nextState}`);
      }

      const previous = state;
      state = nextState;
      logger.info?.("[state-transition]", { from: previous, to: nextState, ...meta });
      onTransition({ from: previous, to: nextState, meta });
      return state;
    },
  };
}
