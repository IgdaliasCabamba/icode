from klein import Klein
import threading

app = Klein()

from twisted.web import server, resource
from twisted.internet import reactor, endpoints

@app.route('/')
def home(request):
    return 'Hello, world!'


def serve(port):
    site = server.Site(app.resource())
    endpoint = endpoints.TCP6ServerEndpoint(reactor, port)
    endpoint.listen(site)

def run_reactor():
    print("Runing")
    reactor.run(installSignalHandlers=False)    

thread = threading.Thread(target=run_reactor, daemon = False)
thread.start()

thread1 = threading.Thread(target=serve, args=(8080, ), daemon = False)
thread1.start()

thread2 = threading.Thread(target=serve, args=(8081, ), daemon = False)
thread2.start()
