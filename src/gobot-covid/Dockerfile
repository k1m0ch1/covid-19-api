FROM golang:1.14-alpine AS builder

# Install OS level dependencies
RUN apk add --update alpine-sdk git && \
	git config --global http.https://gopkg.in.followRedirects true

WORKDIR /go/src/github.com/k1m0ch1/covid-19-api/
COPY ./ .

RUN go build -o covid

FROM alpine:3.8
WORKDIR /go/src/github.com/k1m0ch1/covid-19-api/
COPY --from=builder /go/src/github.com/k1m0ch1/covid-19-api /go/src/github.com/k1m0ch1/covid-19-api
COPY --from=builder /go/src/github.com/k1m0ch1/covid-19-api/covid /bin/covid

ENTRYPOINT ["/bin/covid"]
