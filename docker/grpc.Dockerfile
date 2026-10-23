
FROM golang:1.22-alpine AS builder
WORKDIR /src

COPY go.mod ./
COPY go.sum* ./
RUN go mod tidy

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/grpcserver ./cmd/grpcserver

FROM alpine:3.20
WORKDIR /app
COPY --from=builder /out/grpcserver /app/grpcserver

EXPOSE 9090

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
    CMD nc -z localhost 9090 || exit 1

ENTRYPOINT ["/app/grpcserver", "-addr", ":9090", "-data", "/app/data"]
