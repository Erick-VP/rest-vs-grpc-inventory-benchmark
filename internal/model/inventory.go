package model

type Location struct {
	WarehouseID   string `json:"warehouse_id"`
	WarehouseName string `json:"warehouse_name"`
	SectorID      string `json:"sector_id"`
	SectorName    string `json:"sector_name"`
	Aisle         string `json:"aisle"`
	Shelf         string `json:"shelf"`
}
type Timestamps struct {
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}
type Item struct {
	ItemID      string     `json:"item_id"`
	SKU         string     `json:"sku"`
	ProductName string     `json:"product_name"`
	Category    string     `json:"category"`
	Quantity    int32      `json:"quantity"`
	UnitPrice   float64    `json:"unit_price"`
	Location    Location   `json:"location"`
	Timestamps  Timestamps `json:"timestamps"`
}
type AggregateInventoryResponse struct {
	Items      []Item `json:"items"`
	TotalCount int    `json:"total_count"`
}
