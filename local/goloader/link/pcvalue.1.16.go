//go:build go1.16 && !go1.99
// +build go1.16,!go1.99

package link

import "github.com/pkujhd/goloader/obj"

func adaptPCFile(linker *Linker, symbol *obj.ObjSymbol) {
}
