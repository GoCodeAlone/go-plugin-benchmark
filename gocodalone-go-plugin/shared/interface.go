package shared

import (
	"context"

	gocplugin "github.com/GoCodeAlone/go-plugin"
	"github.com/uberswe/go-plugin-benchmark/gocodalone-go-plugin/proto"
	"google.golang.org/grpc"
)

// Handshake is a common handshake that is shared by plugin and host.
var Handshake = gocplugin.HandshakeConfig{
	ProtocolVersion:  1,
	MagicCookieKey:   "RANDINT_PLUGIN",
	MagicCookieValue: "randint",
}

// PluginMap is the map of plugins we can dispense.
var PluginMap = map[string]gocplugin.Plugin{
	"randint_grpc": &RandIntPlugin{},
}

// RandIntProvider is the interface that we're exposing as a plugin.
type RandIntProvider interface {
	RandInt() int64
}

// RandIntPlugin is the implementation of plugin.Plugin so we can serve/consume this.
type RandIntPlugin struct {
	gocplugin.Plugin
	Impl RandIntProvider
}

func (p *RandIntPlugin) GRPCServer(broker *gocplugin.GRPCBroker, s *grpc.Server) error {
	proto.RegisterRandIntServiceServer(s, &GRPCServer{Impl: p.Impl})
	return nil
}

func (p *RandIntPlugin) GRPCClient(_ context.Context, _ *gocplugin.GRPCBroker, c *grpc.ClientConn) (any, error) {
	return &GRPCClient{client: proto.NewRandIntServiceClient(c)}, nil
}

// GRPCServer is the gRPC server that GRPCClient talks to.
type GRPCServer struct {
	proto.UnimplementedRandIntServiceServer
	Impl RandIntProvider
}

func (s *GRPCServer) RandInt(_ context.Context, _ *proto.RandIntRequest) (*proto.RandIntResponse, error) {
	return &proto.RandIntResponse{Value: s.Impl.RandInt()}, nil
}

// GRPCClient is an implementation of RandIntProvider that talks over RPC.
type GRPCClient struct {
	client proto.RandIntServiceClient
}

func (c *GRPCClient) RandInt() int64 {
	resp, err := c.client.RandInt(context.Background(), &proto.RandIntRequest{})
	if err != nil {
		panic(err)
	}
	return resp.Value
}
