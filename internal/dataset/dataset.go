package dataset

import (
	"fmt"
	"path/filepath"
	"strconv"
	"strings"
)

var Files = map[int]string{
	1000:   "inventory_1000.json",
	10000:  "inventory_10000.json",
	50000:  "inventory_50000.json",
	100000: "inventory_100000.json",
}

func NormalizeSize(raw string) (int, error) {
	raw = strings.TrimSpace(strings.ToLower(raw))
	if raw == "" {
		return 0, fmt.Errorf("parâmetro 'size' ausente")
	}

	if strings.HasSuffix(raw, "k") {
		numPart := strings.TrimSuffix(raw, "k")
		n, err := strconv.Atoi(numPart)
		if err != nil {
			return 0, fmt.Errorf("valor de 'size' inválido: %q", raw)
		}
		return n * 1000, nil
	}

	n, err := strconv.Atoi(raw)
	if err != nil {
		return 0, fmt.Errorf("valor de 'size' inválido: %q", raw)
	}
	return n, nil
}
func Path(dataDir string, size int) (path string, ok bool) {
	filename, ok := Files[size]
	if !ok {
		return "", false
	}
	return filepath.Join(dataDir, filename), true
}
