package main

import (
	"math/rand"
	"os"

	gocplugin "github.com/GoCodeAlone/go-plugin"
	"github.com/uberswe/go-plugin-benchmark/gocodalone-go-plugin/shared"
	"github.com/hashicorp/go-hclog"
)

// RandIntImpl is the concrete implementation of RandIntProvider.
type RandIntImpl struct{}

func (r *RandIntImpl) RandInt() int64 {
	return int64(rand.Int())
}

func main() {
	logger := hclog.New(&hclog.LoggerOptions{
		Name:   "randint-plugin",
		Output: os.Stdout,
		Level:  hclog.Off,
	})

	gocplugin.Serve(&gocplugin.ServeConfig{
		HandshakeConfig: shared.Handshake,
		Plugins: map[string]gocplugin.Plugin{
			"randint_grpc": &shared.RandIntPlugin{Impl: &RandIntImpl{}},
		},
		GRPCServer: gocplugin.DefaultGRPCServer,
		Logger:     logger,
	})
}
