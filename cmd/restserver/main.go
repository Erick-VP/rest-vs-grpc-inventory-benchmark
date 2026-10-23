package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"inventory-benchmark/internal/dataset"
	"inventory-benchmark/internal/model"
)

func inventoryHandler(dataDir string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		sizeParam := r.URL.Query().Get("size")
		size, err := dataset.NormalizeSize(sizeParam)
		if err != nil {
			writeError(w, http.StatusBadRequest, err.Error())
			return
		}

		path, ok := dataset.Path(dataDir, size)
		if !ok {
			writeError(w, http.StatusBadRequest,
				fmt.Sprintf("size %d não suportado; valores aceitos: 1000, 10000, 50000, 100000", size))
			return
		}

		raw, err := os.ReadFile(path)
		if err != nil {
			log.Printf("erro ao ler %s: %v", path, err)
			writeError(w, http.StatusInternalServerError, "falha ao ler dataset")
			return
		}
		var payload model.AggregateInventoryResponse
		if err := json.Unmarshal(raw, &payload); err != nil {
			log.Printf("erro ao desserializar %s: %v", path, err)
			writeError(w, http.StatusInternalServerError, "falha ao desserializar dataset")
			return
		}
		out, err := json.Marshal(payload)
		if err != nil {
			log.Printf("erro ao serializar resposta: %v", err)
			writeError(w, http.StatusInternalServerError, "falha ao serializar resposta")
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Content-Length", strconv.Itoa(len(out)))
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write(out)
	}
}

func writeError(w http.ResponseWriter, status int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]string{"error": message})
}
func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func main() {
	addr := flag.String("addr", ":8080", "endereço de escuta do servidor HTTP")
	dataDir := flag.String("data", "data", "diretório contendo os datasets JSON gerados pelo cmd/datagen")
	flag.Parse()
	for size := range dataset.Files {
		path, _ := dataset.Path(*dataDir, size)
		if _, err := os.Stat(path); err != nil {
			log.Fatalf("dataset ausente para size=%d (%s): %v — rode 'go run ./cmd/datagen' primeiro", size, path, err)
		}
	}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/v1/inventory", inventoryHandler(*dataDir))
	mux.HandleFunc("GET /healthz", healthHandler)

	server := &http.Server{
		Addr:              *addr,
		Handler:           mux,
		ReadTimeout:       10 * time.Second,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	log.Printf("REST server (JSON/HTTP1.1) ouvindo em %s", *addr)
	log.Printf("dataset dir: %s", *dataDir)
	log.Printf("endpoint: GET %s/api/v1/inventory?size={1000|10000|50000|100000}", *addr)

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("erro ao iniciar servidor: %v", err)
	}
}
