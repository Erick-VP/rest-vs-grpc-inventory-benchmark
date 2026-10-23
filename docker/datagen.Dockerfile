
FROM golang:1.22-alpine AS builder
WORKDIR /src

COPY go.mod ./
COPY go.sum* ./
RUN go mod tidy

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/datagen ./cmd/datagen

FROM alpine:3.20
WORKDIR /app
COPY --from=builder /out/datagen /app/datagen

ENTRYPOINT ["/app/datagen"]
