from scrap import service


def main():
    wsgi_service = service.WSGIService()
    wsgi_service.start()
