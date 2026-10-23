import grpc from 'k6/net/grpc';
import { check } from 'k6';
import { buildScenarios, MAX_MESSAGE_SIZE } from './common.js';

const GRPC_ADDR = __ENV.GRPC_ADDR || 'localhost:9090';

const client = new grpc.Client();
let connected = false;

export const options = {
	scenarios: buildScenarios('aggregate'),
	thresholds: {
		checks: ['rate==1'],
	},
};

export function aggregate() {
	if (!connected) {
		client.connect(GRPC_ADDR, {
			plaintext: true,
			reflect: true,
			// Os limites do cliente são independentes dos do servidor e precisam comportar 100 mil registros.
			maxReceiveSize: MAX_MESSAGE_SIZE,
			maxSendSize: MAX_MESSAGE_SIZE,
		});
		connected = true;
	}

	const size = Number(__ENV.SIZE);

	const res = client.invoke(
		'inventory.InventoryService/AggregateInventory',
		{ limit: size },
		{ tags: { size: String(size) } }
	);

	check(res, {
		'status é OK': (r) => r && r.status === grpc.StatusOK,
		'totalCount bate com o size solicitado': (r) =>
			r && r.message && r.message.totalCount === size,
	});
}
