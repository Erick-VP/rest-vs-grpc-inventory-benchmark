
FROM golang:1.22-alpine AS builder
WORKDIR /src

COPY go.mod ./
COPY go.sum* ./
RUN go mod tidy

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/restserver ./cmd/restserver

FROM alpine:3.20
WORKDIR /app
COPY --from=builder /out/restserver /app/restserver

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
    CMD wget -qO- http://localhost:8080/healthz || exit 1

ENTRYPOINT ["/app/restserver", "-addr", ":8080", "-data", "/app/data"]
