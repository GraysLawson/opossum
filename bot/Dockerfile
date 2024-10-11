ARG GO_VERSION=1.20
FROM golang:${GO_VERSION}-bookworm as builder

WORKDIR /bot
COPY . .
COPY ../common /bot/common

WORKDIR /bot
RUN go mod download && go mod verify
RUN go build -v -o /run-app ./cmd/main.go

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=builder /run-app /usr/local/bin/

WORKDIR /usr/local/bin
CMD ["run-app"]
