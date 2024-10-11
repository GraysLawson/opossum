ARG GO_VERSION=1.20
FROM golang:${GO_VERSION}-bookworm as builder

WORKDIR /bot
COPY go.mod go.sum ./
RUN go mod download && go mod verify
COPY . .
RUN go build -v -o /run-app ./cmd/main.go

FROM debian:bookworm-slim
FROM debian:bookworm
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=builder /run-app /usr/local/bin/

WORKDIR /usr/local/bin
CMD ["run-app"]
