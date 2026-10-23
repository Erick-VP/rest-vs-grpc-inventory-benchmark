export const SIZES = [1000, 10000, 50000, 100000];
export const VUS = Number(__ENV.VUS || 10);
export const SCENARIO_DURATION = __ENV.DURATION || '30s';
export const GRACEFUL_STOP = __ENV.GRACEFUL_STOP || '5s';
export const MAX_MESSAGE_SIZE = Number(__ENV.MAX_MESSAGE_SIZE || 64 * 1024 * 1024);
const REQUESTED_SIZES = __ENV.SIZE ? [Number(__ENV.SIZE)] : SIZES;

function durationToSeconds(d) {
	const match = /^(\d+)(ms|s|m|h)$/.exec(d);
	if (!match) return 30;
	const value = Number(match[1]);
	const factor = { ms: 0.001, s: 1, m: 60, h: 3600 }[match[2]];
	return value * factor;
}
export function buildScenarios(execName) {
	const scenarios = {};
	const stepSeconds =
		durationToSeconds(SCENARIO_DURATION) + durationToSeconds(GRACEFUL_STOP) + 5;

	REQUESTED_SIZES.forEach((size, idx) => {
		scenarios[`size_${size}`] = {
			executor: 'constant-vus',
			vus: VUS,
			duration: SCENARIO_DURATION,
			gracefulStop: GRACEFUL_STOP,
			exec: execName,
			startTime: `${idx * stepSeconds}s`,
			env: { SIZE: String(size) },
			tags: { size: String(size) },
		};
	});

	return scenarios;
}
