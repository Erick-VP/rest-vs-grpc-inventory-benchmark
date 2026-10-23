import http from 'k6/http';
import { check } from 'k6';
import { buildScenarios } from './common.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
	scenarios: buildScenarios('aggregate'),
	thresholds: {
		http_req_failed: ['rate==0'],
		checks: ['rate==1'],
	},
};

export function aggregate() {
	const size = __ENV.SIZE;

	const res = http.get(`${BASE_URL}/api/v1/inventory?size=${size}`, {
		tags: { size },
	});

	check(res, {
		'status é 200': (r) => r.status === 200,
		'content-type é application/json': (r) =>
			(r.headers['Content-Type'] || '').includes('application/json'),
		'total_count bate com o size solicitado': (r) => {
			try {
				return r.json('total_count') === Number(size);
			} catch (e) {
				return false;
			}
		},
	});
}
