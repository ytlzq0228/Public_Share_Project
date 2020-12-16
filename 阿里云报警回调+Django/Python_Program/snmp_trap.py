# Notification Originator Application (TRAP)
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import encoder
from pysnmp.proto import api
import sys
from save_log import save_log

def sent_snmp_trap(product,level,regionId,instanceName,name):
	# Protocol version to use
	verID = api.protoVersion2c
	pMod = api.protoModules[verID]
	
	# Build PDU
	trapPDU = pMod.TrapPDU()
	pMod.apiTrapPDU.setDefaults(trapPDU)
	
	# Traps have quite different semantics among proto versions
	if verID == api.protoVersion2c:
	
		var = []
		oid = (1, 3, 6, 1, 4, 1,12149,1)
		val = pMod.OctetString('product:%s'%product)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,2)
		val = pMod.OctetString('level:%s'%level)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,3)
		val = pMod.OctetString('regionId:%s'%regionId)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,4)
		val = pMod.OctetString('instanceName:%s'%instanceName)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,5)
		val = pMod.OctetString('name:%s'%name)
		var.append((oid, val))
		pMod.apiTrapPDU.setVarBinds(trapPDU, var)
		
	print(var)
	save_log(str(var))
	# Build message
	trapMsg = pMod.Message()

	pMod.apiMessage.setDefaults(trapMsg)
	pMod.apiMessage.setCommunity(trapMsg, 'public')
	pMod.apiMessage.setPDU(trapMsg, trapPDU)

	transportDispatcher = AsynsockDispatcher()
	transportDispatcher.registerTransport(
		udp.domainName, udp.UdpSocketTransport().openClientMode()
		)
	transportDispatcher.sendMessage(
		encoder.encode(trapMsg), udp.domainName, ('localhost', 162)
		)
	transportDispatcher.runDispatcher()
	transportDispatcher.closeDispatcher()


if __name__ == '__main__':
	sent_snmp_trap('product2','level22','regionId222','instanceName2222','name22222')
