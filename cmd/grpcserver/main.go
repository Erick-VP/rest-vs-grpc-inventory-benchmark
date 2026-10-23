package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net"
	"os"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"

	"inventory-benchmark/internal/dataset"
	"inventory-benchmark/internal/model"
	"inventory-benchmark/proto/pb"
)

// O payload de 100 mil registros excede o limite padrão de recebimento de 4 MiB; usamos 64 MiB.
const maxMsgSize = 64 * 1024 * 1024

type inventoryServer struct {
	pb.UnimplementedInventoryServiceServer
	dataDir string
}

func (s *inventoryServer) AggregateInventory(ctx context.Context, req *pb.AggregateInventoryRequest) (*pb.AggregateInventoryResponse, error) {
	size := int(req.GetLimit())

	path, ok := dataset.Path(s.dataDir, size)
	if !ok {
		return nil, status.Errorf(codes.InvalidArgument,
			"size %d não suportado; valores aceitos: 1000, 10000, 50000, 100000", size)
	}

	raw, err := os.ReadFile(path)
	if err != nil {
		log.Printf("erro ao ler %s: %v", path, err)
		return nil, status.Error(codes.Internal, "falha ao ler dataset")
	}
	var payload model.AggregateInventoryResponse
	if err := json.Unmarshal(raw, &payload); err != nil {
		log.Printf("erro ao desserializar %s: %v", path, err)
		return nil, status.Error(codes.Internal, "falha ao desserializar dataset")
	}

	resp := &pb.AggregateInventoryResponse{
		Items:      make([]*pb.Item, 0, len(payload.Items)),
		TotalCount: int32(payload.TotalCount),
	}
	for _, item := range payload.Items {
		resp.Items = append(resp.Items, toProtoItem(item))
	}

	return resp, nil
}
func toProtoItem(m model.Item) *pb.Item {
	return &pb.Item{
		ItemId:      m.ItemID,
		Sku:         m.SKU,
		ProductName: m.ProductName,
		Category:    m.Category,
		Quantity:    m.Quantity,
		UnitPrice:   m.UnitPrice,
		Location: &pb.Location{
			WarehouseId:   m.Location.WarehouseID,
			WarehouseName: m.Location.WarehouseName,
			SectorId:      m.Location.SectorID,
			SectorName:    m.Location.SectorName,
			Aisle:         m.Location.Aisle,
			Shelf:         m.Location.Shelf,
		},
		Timestamps: &pb.Timestamps{
			CreatedAt: m.Timestamps.CreatedAt,
			UpdatedAt: m.Timestamps.UpdatedAt,
		},
	}
}

func main() {
	addr := flag.String("addr", ":9090", "endereço de escuta do servidor gRPC")
	dataDir := flag.String("data", "data", "diretório contendo os datasets JSON gerados pelo cmd/datagen")
	flag.Parse()
	for size := range dataset.Files {
		path, _ := dataset.Path(*dataDir, size)
		if _, err := os.Stat(path); err != nil {
			log.Fatalf("dataset ausente para size=%d (%s): %v — rode 'go run ./cmd/datagen' primeiro", size, path, err)
		}
	}

	lis, err := net.Listen("tcp", *addr)
	if err != nil {
		log.Fatalf("falha ao abrir listener em %s: %v", *addr, err)
	}

	grpcServer := grpc.NewServer(
		grpc.MaxRecvMsgSize(maxMsgSize),
		grpc.MaxSendMsgSize(maxMsgSize),
	)

	pb.RegisterInventoryServiceServer(grpcServer, &inventoryServer{dataDir: *dataDir})
	reflection.Register(grpcServer)

	log.Printf("gRPC server (Protobuf/HTTP2) ouvindo em %s", *addr)
	log.Printf("dataset dir: %s", *dataDir)
	log.Printf("max message size (send/recv): %d bytes (%.0f MiB)", maxMsgSize, float64(maxMsgSize)/(1024*1024))
	log.Printf("método: inventory.InventoryService/AggregateInventory (limit={1000|10000|50000|100000})")

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf(fmt.Sprintf("erro ao iniciar servidor gRPC: %v", err))
	}
}
