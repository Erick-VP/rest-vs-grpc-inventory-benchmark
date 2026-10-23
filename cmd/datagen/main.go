package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"time"

	"inventory-benchmark/internal/model"
)

const seed = 42

var volumes = []int{1000, 10000, 50000, 100000}

var warehouseNames = []string{
	"Centro de Distribuição Norte",
	"Centro de Distribuição Sul",
	"Armazém Central",
	"Hub Logístico Leste",
	"Hub Logístico Oeste",
}

var sectorNames = []string{
	"Eletrônicos", "Eletrodomésticos", "Vestuário", "Calçados",
	"Móveis", "Brinquedos", "Ferramentas", "Alimentos",
	"Higiene e Beleza", "Papelaria",
}

var categories = []string{
	"Eletrônicos", "Eletrodomésticos", "Moda", "Casa e Decoração",
	"Esporte e Lazer", "Ferramentas", "Alimentício", "Beleza",
	"Papelaria", "Brinquedos",
}

var productAdjectives = []string{
	"Premium", "Standard", "Compacto", "Pro", "Lite", "Max",
	"Plus", "Essential", "Ultra", "Basic",
}

var productNouns = []string{
	"Smartphone", "Notebook", "Cadeira", "Mesa", "Tênis", "Camiseta",
	"Furadeira", "Liquidificador", "Fone de Ouvido", "Monitor",
	"Mochila", "Panela", "Ventilador", "Livro", "Caderno",
}

func randomChoice(r *rand.Rand, options []string) string {
	return options[r.Intn(len(options))]
}
func randomTimestamp(r *rand.Rand, base time.Time) string {
	offset := time.Duration(r.Intn(730*24)) * time.Hour
	return base.Add(-offset).Format(time.RFC3339)
}

func generateItem(r *rand.Rand, index int, base time.Time) model.Item {
	warehouseIdx := r.Intn(len(warehouseNames))
	sectorIdx := r.Intn(len(sectorNames))

	warehouseID := fmt.Sprintf("WH-%02d", warehouseIdx+1)
	sectorID := fmt.Sprintf("SEC-%02d", sectorIdx+1)

	createdAt := randomTimestamp(r, base)
	updatedAt := randomTimestamp(r, base)

	productName := fmt.Sprintf("%s %s %04d",
		randomChoice(r, productNouns),
		randomChoice(r, productAdjectives),
		r.Intn(9999),
	)

	return model.Item{
		ItemID:      fmt.Sprintf("ITEM-%08d", index),
		SKU:         fmt.Sprintf("SKU-%06d-%03d", index, r.Intn(999)),
		ProductName: productName,
		Category:    randomChoice(r, categories),
		Quantity:    int32(r.Intn(500)),
		UnitPrice:   roundToCents(r.Float64()*4990 + 10),
		Location: model.Location{
			WarehouseID:   warehouseID,
			WarehouseName: warehouseNames[warehouseIdx],
			SectorID:      sectorID,
			SectorName:    sectorNames[sectorIdx],
			Aisle:         fmt.Sprintf("A-%02d", r.Intn(40)+1),
			Shelf:         fmt.Sprintf("P-%02d", r.Intn(12)+1),
		},
		Timestamps: model.Timestamps{
			CreatedAt: createdAt,
			UpdatedAt: updatedAt,
		},
	}
}

func roundToCents(v float64) float64 {
	return float64(int(v*100)) / 100
}

func generateDataset(volume int) model.AggregateInventoryResponse {
	r := rand.New(rand.NewSource(seed + int64(volume)))
	base := time.Date(2026, 7, 1, 0, 0, 0, 0, time.UTC)

	items := make([]model.Item, 0, volume)
	for i := 1; i <= volume; i++ {
		items = append(items, generateItem(r, i, base))
	}

	return model.AggregateInventoryResponse{
		Items:      items,
		TotalCount: volume,
	}
}

func main() {
	outDir := "data"
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		fmt.Fprintf(os.Stderr, "erro ao criar diretório %s: %v\n", outDir, err)
		os.Exit(1)
	}

	for _, volume := range volumes {
		dataset := generateDataset(volume)

		payload, err := json.Marshal(dataset)
		if err != nil {
			fmt.Fprintf(os.Stderr, "erro ao serializar volume %d: %v\n", volume, err)
			os.Exit(1)
		}

		filename := filepath.Join(outDir, fmt.Sprintf("inventory_%d.json", volume))
		if err := os.WriteFile(filename, payload, 0o644); err != nil {
			fmt.Fprintf(os.Stderr, "erro ao gravar %s: %v\n", filename, err)
			os.Exit(1)
		}

		sizeMB := float64(len(payload)) / (1024 * 1024)
		fmt.Printf("gerado: %-28s | registros: %-7d | tamanho: %8.2f MB\n", filename, volume, sizeMB)
	}
}
