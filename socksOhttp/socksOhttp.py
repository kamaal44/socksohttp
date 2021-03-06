import logging

from socksohttp.server import *
from socksohttp.client import *
from socksohttp import logger
from socksohttp.socksetio_proxy import *


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Socks5 over HTTP')
	parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity, can be stacked')

	subparsers = parser.add_subparsers(help = 'commands')
	subparsers.required = True
	subparsers.dest = 'mode'

	server_group = subparsers.add_parser('server', help='Server mode')
	server_group.add_argument('listen_ip', help='IP to listen on')
	server_group.add_argument('listen_port', type=int, help='port for the server')
	server_group.add_argument('-j', action='store_true', help='spin up proxy JS server')
	server_group.add_argument('-s', action='store_true', help='spin up proxy Socket.IO server')
	
	agent_group = subparsers.add_parser('agent', help='Agent mode')
	agent_group.add_argument('url', help='URL to connect to')
	agent_group.add_argument('-p','--proxy', help='Proxy server url')
	agent_group.add_argument('-pi','--proxy-ip', help='IP the proxy should listen on', default = '127.0.0.1')
	agent_group.add_argument('-pp','--proxy-port', type=int, help='Port the proxy should listen on', default = '10001')

	special_group = subparsers.add_parser('special', help='Special Agent mode')
	special_group.add_argument('-l','--listen-ip', help='Ip to listen for incoming connections')
	special_group.add_argument('-p','--listen-port', help='Port to listen for incoming connections')

	args = parser.parse_args()
	print(args)

	if args.verbose == 0:
		logging.basicConfig(level=logging.INFO)
		wslogger = logging.getLogger('websockets')
		wslogger.setLevel(logging.ERROR)
		wslogger.addHandler(logging.StreamHandler())
		
	elif args.verbose == 1:
		logging.basicConfig(level=logging.DEBUG)
		logger.setLevel(logging.INFO)
		wslogger = logging.getLogger('websockets')
		wslogger.setLevel(logging.INFO)
		wslogger.addHandler(logging.StreamHandler())
		
	else:
		logging.basicConfig(level=1)
		logger.setLevel(logging.DEBUG)
		wslogger = logging.getLogger('websockets')
		wslogger.setLevel(logging.DEBUG)
		wslogger.addHandler(logging.StreamHandler())


	if args.mode == 'server':
		logging.debug('Starting server mode')
		if args.s == True:
			s = SocketIOProxy(server_url = 'ws://127.0.0.1:8443',host = '0.0.0.0', port = '80', logger = logger)
			asyncio.ensure_future(s.run())
		cs = CommsServer(args.listen_ip, int(args.listen_port), args.j)
		start_server = cs.run()
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()

	elif args.mode == 'agent':
		logging.debug('Starting agent mode')
		ca = CommsAgentServer(args.url, args.proxy, args.proxy_ip, args.proxy_port)
		asyncio.get_event_loop().run_until_complete(ca.run())
		logging.debug('Agent exited!')

	elif args.mode == 'special':
		logging.debug('Starting special agent mode')
		if args.listen_ip and args.listen_port:
			ca = CommsAgentServerListening(args.listen_ip, args.listen_port)
		else:
			ca = CommsAgentServerListening()
		asyncio.get_event_loop().run_until_complete(ca.run())
		asyncio.get_event_loop().run_forever()
		logging.debug('Agent exited!')