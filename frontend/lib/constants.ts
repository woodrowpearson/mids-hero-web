/**
 * Application constants
 * Game rules, configuration values, and magic numbers
 */

/**
 * City of Heroes game rules
 */
export const GAME_RULES = {
  /** Maximum number of slots per power */
  MAX_SLOTS_PER_POWER: 6,

  /** Maximum character level */
  MAX_CHARACTER_LEVEL: 50,

  /** Minimum character level */
  MIN_CHARACTER_LEVEL: 1,

  /** Number of pool power slots available */
  NUM_POOL_POWERSETS: 4,
} as const;

/**
 * UI and performance configuration
 */
export const UI_CONFIG = {
  /** Debounce time for auto-calculation (milliseconds) */
  AUTO_CALCULATE_DEBOUNCE_MS: 200,

  /** Default number of columns for power display */
  DEFAULT_COLUMN_LAYOUT: 3,

  /** Minimum number of columns */
  MIN_COLUMNS: 2,

  /** Maximum number of columns */
  MAX_COLUMNS: 6,
} as const;

/**
 * API configuration
 */
export const API_CONFIG = {
  /** Request timeout in milliseconds */
  TIMEOUT_MS: 10000,

  /** Default stale time for TanStack Query (milliseconds) */
  DEFAULT_STALE_TIME_MS: 5 * 60 * 1000, // 5 minutes

  /** Number of retries for failed requests */
  DEFAULT_RETRY_COUNT: 1,
} as const;

/**
 * Storage keys for localStorage
 */
export const STORAGE_KEYS = {
  /** Character build data */
  CHARACTER_BUILD: "character-build-storage",

  /** UI preferences */
  UI_PREFERENCES: "ui-preferences-storage",

  /** Auth token (future) */
  AUTH_TOKEN: "auth_token",
} as const;
